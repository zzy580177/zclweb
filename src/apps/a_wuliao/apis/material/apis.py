from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses
from django.db.models import Count, Q, F, Value, Max
from django.db.models.functions import Concat
from django.db.models.expressions import ExpressionWrapper
from django.db.models import IntegerField
from django.db import transaction

from apps.a_wuliao.models import *
from apps.a_wuliao.apis.material.schemas import *

router = Router(tags=['material'])

@router.post('/material', url_name='a_wuliao/material/create')
def create(request, payload: list[MaterialIn]):
    success = []
    faileds = []
    errors = []
    existCnt = 0
    try:          
        target_group_numbers = {item.number.rsplit('.', 1)[0] for item in payload if '.' in item.number}
        target_material_numbers = {item.number for item in payload} 
        existing_units = {unit.name: unit for unit in Attribute.objects.filter(description = '单位').all()}
        existing_groups = {group.number: group for group in MaterialGroup.objects.filter(number__in=target_group_numbers).all()}
        existing_materials = {material.number: material for material in Material.objects.all()}
        existing_materials_pk = {material.pk: material for material in Material.objects.all()}
    except Exception as e:
        errors.append(f"批量查询失败: {str(e)} ")

    to_create = []
    p_material_map = {}    # 存放 material_number -> resolved 父物料对象（Model 或 None）
    seen_numbers = set()   # 防止 payload 内重复创建同一编号

    for idx, item in enumerate(payload):
        if item.number is None or item.number.strip() == '':
            continue
        try:
            item_dic = {}
            p_material_raw = item.p_material
            item_dic = {k: v for k, v in item.dict().items() if k != 'p_material'}

            parent__number = '.'.join(item.number.split('.')[:-1])
            unit_obj = existing_units.get(item.unit)
            if not unit_obj:
                errors.append(f"{idx+1}: 未找到 属性单位: {item.unit} 请先添加后重试")
                faileds.append({'id': idx, 'status': False, })
                continue
            group_obj = existing_groups.get(parent__number)
            if not group_obj:
                errors.append(f"{idx+1}: 未找到{item.number}-{item.name}父节点")
                faileds.append({'id': idx, 'status': False, })
                continue

            p_material_obj = None
            if p_material_raw is not None and p_material_raw != "":
                p_raw_str = str(p_material_raw)
                if '.' in p_raw_str:
                    p_material_obj = existing_materials.get(p_raw_str)
                    if not p_material_obj:
                        errors.append(f"{idx+1}: 未找到上级物料编号:{p_raw_str} 请先添加后重试")
                        faileds.append({'id': idx, 'status': False})
                        continue
                elif p_raw_str.isdigit():
                    p_material_obj = existing_materials_pk.get(p_raw_str)
                    if not p_material_obj:
                        errors.append(f"{idx+1}: 未找到上级物料ID:{p_raw_str} 请先添加后重试")
                        faileds.append({'id': idx, 'status': False})
                        continue
                else:
                    errors.append(f"{idx+1}: 上级物料:{p_raw_str} 格式错误，请使用物料编号或ID")
                    faileds.append({'id': idx, 'status': False})
                    continue
            item_dic['group'] = group_obj
            item_dic['unit'] = unit_obj
            if item.number in existing_materials or item.number in seen_numbers:
                existCnt += 1
                continue
            seen_numbers.add(item.number)
            to_create.append((idx, item_dic, item.name, p_material_obj))
            p_material_map[item.number] = p_material_obj
        except Exception as e:
            errors.append(f"{idx+1}: 批量查询失败: {str(e)} ")
            faileds.append({'id': idx, 'status': False, })

    if to_create:
        try:
            with transaction.atomic():
                materials = []
                for idx, item_dic, name, _ in to_create:
                    materials.append(Material(**item_dic))
                created_objects = Material.objects.bulk_create(materials)

                bomVersions = []
                boms = []
                for i, obj in enumerate(created_objects):
                    bomVersions.append(BomVersion(material=obj,
                        version="V1.0", change_reason="初始版本创建", status="已发布", creator="管理员"))
                createdBomV_objects = BomVersion.objects.bulk_create(bomVersions)
                material_ids = [obj.pk for obj in created_objects]
                saved_bv_map = {(bv.material_id, bv.version): bv for bv in 
                    BomVersion.objects.filter(material_id__in=material_ids, version="V1.0")}

                for i, obj in enumerate(created_objects):
                    idx, _, name, p_mat_obj = to_create[i]
                    success.append({'id': idx, 'created': True, 'name': obj.name})
                    bv = saved_bv_map.get((obj.pk,"V1.0")) or (createdBomV_objects[i] if i < len(createdBomV_objects) else None)
                    if bv is None or getattr(bv, 'pk', None) is None:
                        raise RuntimeError(f"无法获取已保存的 BomVersion 主键 (material={obj.pk})")
                    boms.append(Bom(version=bv, p_material=p_mat_obj))
                Bom.objects.bulk_create(boms)
            
        except Exception as e:
            errors.append(f"批量创建失败: {str(e)}")
            for idx, _, _, _ in to_create:
                faileds.append({'id': idx, 'status': False})
    
    data = {'faileds': faileds, 'success': success, 'Error': errors}
    data['message'] = f'{len(success)}条记录上传成功, {existCnt}条记录已存在, {len(faileds)}条记录上传失败'
    if(len(errors)>0):
        return {'success': False, 'data': data}
    return {'success': True, 'data': {'message': f'成功上传{len(success)}条记录, {existCnt}条记录已存在'}}

@router.get('/get_material_routes', response=List[MaterilRoutesOut], url_name='a_wuliao/material/get_material_routes')
def get_material_routes(request, material_id: str, version: str, order_id: str = None):
    try:
        # 1. 获取子物料ID列表
        subM = [obj['version__material_id'] for obj in Bom.objects.filter(
            Q(p_material_id=material_id, version__version=version)
        ).values('version__material_id')]

        material_ids = [int(material_id)]  
        for mat_id in subM:
            if mat_id and mat_id not in material_ids:
                material_ids.append(mat_id)
        
        # 2. 获取物料对象
        materials = Material.objects.filter(material_id__in=material_ids)
        
        # 3. 如果提供了order_id，获取ProductionPlan中的route信息
        production_plan_routes = {}
        if order_id:
            try:
                # 查找OrderParts
                from apps.b_jihua.models import OrderParts
                from apps.d_paichan.models import ProductionPlan
                
                # 为每个物料查找对应的ProductionPlan
                for mat_id in material_ids:
                    # 查找OrderParts：通过order_id和material_id
                    order_part = OrderParts.objects.filter(
                        order__order_id=order_id,
                        material_id=mat_id
                    ).first()
                    
                    if order_part:
                        # 查找ProductionPlan
                        production_plan = ProductionPlan.objects.filter(
                            order_part=order_part
                        ).first()
                        
                        if production_plan:
                            production_plan_routes[mat_id] = {
                                'route': production_plan.route_id if production_plan.route else None,
                                'cnc_route': production_plan.cnc_route_id if production_plan.cnc_route else None
                            }
            except Exception as e:
                # 如果查询ProductionPlan失败，继续执行，不影响主要功能
                print(f"查询ProductionPlan失败: {e}")
        
        # 4. 为每个物料对象添加production_plan_routes信息
        # 这里我们需要修改返回的数据结构，但MaterilRoutesOut模式已经支持route和cnc_route字段
        # 这些字段会通过解析器自动填充，但我们需要确保解析器能使用production_plan_routes中的数据
        
        # 由于解析器是静态方法，我们无法直接传递参数
        # 作为替代方案，我们可以为每个物料对象动态添加属性
        for material in materials:
            if material.material_id in production_plan_routes:
                routes_info = production_plan_routes[material.material_id]
                # 动态添加属性，这些属性会被MaterilRoutesOut的解析器使用
                material._production_plan_route = routes_info.get('route')
                material._production_plan_cnc_route = routes_info.get('cnc_route')
            else:
                material._production_plan_route = None
                material._production_plan_cnc_route = None
        
        return materials
    except Exception as e:
        print(f"get_material_routes错误: {e}")
        return []

@router.get('/material', response=List[MaterialSampleOut], url_name='a_wuliao/material/list')
@paginate
def list_items(request, material_model: str = None, material_number: str = None):

    filters = Q()    
    if material_model:
        filters &= Q(model=material_model)
    if material_number:
        filters &= Q(number=material_number)
    if filters:
        qs = Material.objects.filter(filters)
    else:
        qs = Material.objects.all()
    return qs.annotate(material_model=F('model'), 
                       material_number = F('number'), 
                       material_name = F('name'))


@router.put('/material/{item_id}', response=MaterialOut, url_name='a_wuliao/material/update')
def update(request, item_id, payload: MaterialIn):
    item = get_object_or_404(Material, id=item_id)
    for attr, value in payload.dict().items():
        if attr != 'p_material':
            setattr(item, attr, value)
    item.save()
    return item


@router.patch('/material/{item_id}', response=MaterialOut, url_name='a_wuliao/material/partial_update')
def partial_update(request, item_id, payload: MaterialIn):
    item = get_object_or_404(Material, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        if attr != 'p_material':
            setattr(item, attr, value)
    item.save()
    return item


@router.delete('/material/{item_id}', url_name='a_wuliao/material/destroy')
def destroy(request, item_id):
    item = get_object_or_404(Material, id=item_id)
    item.delete()
    return responses.ok('已删除')
