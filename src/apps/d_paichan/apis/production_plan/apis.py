from typing import List

from django.shortcuts import get_object_or_404
from django.db import transaction
from ninja import Router

from django_starter.http.response import responses

from apps.d_paichan.models import ProductionPlan
from apps.d_paichan.apis.production_plan.schemas import *

from apps.a_wuliao.models import Material, Bom, BomVersion
from apps.b_jihua.models import OrderParts
from apps.c_gongyi.models import Route

router = Router(tags=['production_plan'])

@router.post('/production_plan', response=ProductionPlanCreateOut, url_name='d_paichan/production_plan/create')
def create(request, payload: List[ProductionPlanIn]):
    """
    批量创建或更新生产计划
    支持批量处理多个订单零件的生产计划
    如果 order_part 已存在则更新，不存在则创建
    
    注意：
    1. order_part 字段应该是 OrderParts.material_id
    2. payload[0] 默认为主件，其他为子件
    3. 当子件对应的OrderParts未创建时，根据主件构建并创建子件对应的OrderParts
    4. 父子关系在OrderParts中通过p_orderpart字段维护
    """
    created_count = 0
    updated_count = 0
    failed_count = 0
    success_items = []  # 成功的生产计划对象列表
    failed_items = []   # 失败的项目信息
    
    # 验证输入数据
    if not payload:
        return {
            'success': False,
            'data': [],
            'failed_items': ['请求数据为空'],
            'message': '未提供生产计划数据'
        }
    
    try:
        with transaction.atomic():
            # 获取主件（第一个元素）
            main_item_data = payload[0]
            main_order_part = None
            
            # 首先处理主件
            for index, item_data in enumerate(payload):
                try:
                    # 验证必需字段
                    if not item_data.order_part:
                        failed_count += 1
                        failed_items.append(f'第{index+1}项: 订单零件ID为空，跳过处理')
                        continue
                    
                    if not item_data.order_id:
                        failed_count += 1
                        failed_items.append(f'第{index+1}项: 订单ID为空，跳过处理')
                        continue
                    
                    # 获取或创建订单零件
                    order_part = None
                    is_main_part = (index == 0)  # 第一个是主件
                    
                    try:
                        # 尝试获取现有的OrderParts
                        order_part = OrderParts.objects.get(
                            material_id=item_data.order_part, 
                            order_id=item_data.order_id
                        )
                        
                        # 如果是子件且已有OrderParts，检查是否需要更新p_orderpart
                        if not is_main_part and main_order_part and not order_part.p_orderpart:
                            order_part.p_orderpart = main_order_part
                            order_part.save()
                            
                    except OrderParts.DoesNotExist:
                        # 如果OrderParts不存在
                        if is_main_part:
                            # 主件必须存在
                            failed_count += 1
                            failed_items.append(f'主件订单零件ID {item_data.order_part} (订单: {item_data.order_id}) 不存在')
                            continue
                        else:
                            # 子件不存在，需要根据主件创建
                            if not main_order_part:
                                failed_count += 1
                                failed_items.append(f'子件 {item_data.order_part} 无法创建: 主件未找到或处理失败')
                                continue
                            
                            # 从BOM表获取数量关系
                            bom_quantity = Bom.objects.filter(
                                p_material_id=main_item_data.order_part,  # 主件material_id
                                version__material_id=item_data.order_part  # 子件material_id
                            ).values('quantity').first()
                            
                            # 计算子件数量 = 主件数量 × BOM数量（默认为1）
                            quantity_multiplier = bom_quantity['quantity'] if bom_quantity else 1
                            child_quantity = main_order_part.quantity * quantity_multiplier
                            
                            # 创建子件OrderParts，设置p_orderpart为主件
                            order_part = OrderParts.objects.create(
                                order_id=item_data.order_id,
                                material_id=item_data.order_part,
                                p_orderpart=main_order_part,  # 设置父子关系，同时标识为中间件
                                version=main_order_part.version,
                                status=main_order_part.status,
                                deadline=main_order_part.deadline,
                                quantity=child_quantity,
                                description=f'由主件 {main_item_data.order_part} 自动创建'
                            )
                    
                    # 保存主件引用
                    if is_main_part:
                        main_order_part = order_part
                    
                    # 获取工艺路线（如果提供）
                    route = None
                    cnc_route = None
                    
                    if item_data.route:
                        try:
                            route = Route.objects.get(id=item_data.route, is_cnc=False)
                        except Route.DoesNotExist:
                            failed_count += 1
                            failed_items.append(f'第{index+1}项: 工艺路线ID {item_data.route} 不存在或不是非CNC路线')
                            continue
                    
                    if item_data.cnc_route:
                        try:
                            cnc_route = Route.objects.get(id=item_data.cnc_route, is_cnc=True)
                        except Route.DoesNotExist:
                            failed_count += 1
                            failed_items.append(f'第{index+1}项: CNC工艺路线ID {item_data.cnc_route} 不存在或不是CNC路线')
                            continue
                    
                    # 检查是否已存在生产计划
                    try:
                        existing_plan = ProductionPlan.objects.get(order_part=order_part)
                        
                        # 更新现有记录
                        if route is not None:
                            existing_plan.route = route
                        if cnc_route is not None:
                            existing_plan.cnc_route = cnc_route
                        status_list = ['工艺' ,'CNC工艺', '排产']
                        if existing_plan.route is not None:
                            status_list.remove('工艺')
                        if existing_plan.cnc_route is not None:
                            status_list.remove('CNC工艺')
                        status = f'等待 {", ".join(status_list)}设定'
                        
                        existing_plan.status = status
                        existing_plan.description = item_data.description
                        existing_plan.save()
                        
                        updated_count += 1
                        success_items.append(existing_plan)  # 添加更新后的对象到成功列表
                        
                    except ProductionPlan.DoesNotExist:
                        status_list = ['工艺' ,'CNC工艺', '排产']
                        if route is not None:
                            status_list.remove('工艺')
                        if cnc_route is not None:
                            status_list.remove('CNC工艺')
                        status = f'等待 {", ".join(status_list)}设定'
                        # 创建新记录
                        new_plan = ProductionPlan.objects.create(
                            order_part=order_part,
                            route=route,
                            cnc_route=cnc_route,
                            status = status,
                            description=item_data.description
                        )
                        
                        created_count += 1
                        success_items.append(new_plan)  # 添加新创建的对象到成功列表
                        
                except Exception as e:
                    failed_count += 1
                    failed_items.append(f'第{index+1}项: 订单零件 {item_data.order_part} 处理失败: {str(e)}')
                    # 继续处理其他项目，但事务可能会回滚
        
        # 构建响应
        success_count = created_count + updated_count
        
        if failed_count == 0:
            message = f'成功处理 {success_count} 个生产计划（创建: {created_count}, 更新: {updated_count}）'
            success = True
        elif success_count > 0:
            message = f'部分成功，成功: {success_count} 个，失败: {failed_count} 个'
            success = False
        else:
            message = f'全部失败，共 {failed_count} 个失败项'
            success = False
        
        return {
            'success': success,
            'data': success_items,  # 返回成功的生产计划对象列表
            'failed_items': failed_items,
            'message': message
        }
        
    except Exception as e:
        # 事务级别异常
        return responses.error(f'批量处理生产计划失败: {str(e)}')

@router.get('/production_plan/{item_id}', response=ProductionPlanOut, url_name='d_paichan/production_plan/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(ProductionPlan, id=item_id)
    return item

@router.get('/production_plan', response=List[ProductionPlanOut], url_name='d_paichan/production_plan/list')
def list_items(request):
    qs = ProductionPlan.objects.all()
    return qs

@router.put('/production_plan/{item_id}', response=ProductionPlanOut, url_name='d_paichan/production_plan/update')
def update(request, item_id, payload: ProductionPlanUpdateIn):
    """
    更新生产计划
    只能更新 route, cnc_route, status, description 字段
    order_part 和 order_id 不能通过此接口更新
    """
    item = get_object_or_404(ProductionPlan, id=item_id)
    
    # 只更新允许的字段
    if payload.route is not None:
        try:
            route = Route.objects.get(id=payload.route, is_cnc=False)
            item.route = route
        except Route.DoesNotExist:
            return responses.error(f'工艺路线ID {payload.route} 不存在或不是非CNC路线')
    
    if payload.cnc_route is not None:
        try:
            cnc_route = Route.objects.get(id=payload.cnc_route, is_cnc=True)
            item.cnc_route = cnc_route
        except Route.DoesNotExist:
            return responses.error(f'CNC工艺路线ID {payload.cnc_route} 不存在或不是CNC路线')
    
    if payload.status is not None:
        item.status = payload.status
    
    if payload.description is not None:
        item.description = payload.description
    
    item.save()
    return item

@router.delete('/production_plan/{item_id}', url_name='d_paichan/production_plan/destroy')
def destroy(request, item_id):
    item = get_object_or_404(ProductionPlan, id=item_id)
    item.delete()
    return responses.ok('已删除')
