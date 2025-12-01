from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate
from ninja.security import django_auth
from django.db import transaction
from django.db.models import F, Prefetch, Q

from django_starter.http.response import responses

from apps.c_gongyi.models import *
from apps.c_gongyi.apis.cnc_process.schemas import *
from apps.a_wuliao.models import BomVersion
from apps.b_jihua.models import Order

router = Router(tags=['cnc_process'])


def _check_exist_cnc_route(payload: CNCRouteCreateIn):
    """检查是否存在相同的CNC工艺路线"""
    routes = Route.objects.filter(
        bom_ver__material_id=payload.material_id,
        is_cnc=True
    ).prefetch_related(
        Prefetch('cnc_processes',
            queryset=CNCProcess.objects.order_by('seqnum'))
    )

    for route in routes:
        cnc_processes = list(route.cnc_processes.all().order_by('seqnum'))
        if len(cnc_processes) != len(payload.cnc_processes):
            continue

        # 检查每个CNC工序是否匹配
        all_match = True
        for qs_process, payload_process in zip(cnc_processes, payload.cnc_processes):
            # 获取工序的详细步骤信息
            crafts = CNCCraft.objects.filter(process=qs_process).order_by('step_num')
            qs_step_ids = [craft.step_id for craft in crafts]
            qs_step_parms = [craft.params or {} for craft in crafts]

            payload_step_ids = [int(sid) for sid in payload_process.get('steps_step_ids', [])]  # 转换为整数列表
            payload_step_parms = payload_process.get('steps_parms', [])

            # 比较步骤ID和参数
            if qs_step_ids != payload_step_ids or qs_step_parms != payload_step_parms:
                all_match = False
                break

        if all_match:
            return route

    return None


@router.post('/cnc_process', response=CNCProcessOut, url_name='c_gongyi/cnc_process/create')
def create(request, payload: CNCProcessIn):
    item = CNCProcess.objects.create(**payload.dict())
    return item


@router.get('/cnc_process/{item_id}', response=CNCProcessOut, url_name='c_gongyi/cnc_process/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(CNCProcess, id=item_id)
    return item


@router.get('/cnc_process', response=List[CNCProcessOut], url_name='c_gongyi/cnc_process/list')
@paginate
def list_items(request):
    qs = CNCProcess.objects.all()
    return qs


@router.put('/cnc_process/{item_id}', response=CNCProcessOut, url_name='c_gongyi/cnc_process/update')
def update(request, item_id, payload: CNCProcessIn):
    item = get_object_or_404(CNCProcess, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/cnc_process/{item_id}', response=CNCProcessOut, url_name='c_gongyi/cnc_process/partial_update')
def partial_update(request, item_id, payload: CNCProcessIn):
    item = get_object_or_404(CNCProcess, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/cnc_process/{item_id}', url_name='c_gongyi/cnc_process/destroy')
def destroy(request, item_id):
    item = get_object_or_404(CNCProcess, id=item_id)
    item.delete()
    return responses.ok('已删除')


@router.get('/route/{routeId}', response=List[CNCProcessOut], url_name='c_gongyi/cnc_process/route')
def get_cnc_route(request, routeId: int):
    """获取指定工艺路线的CNC工序数据"""
    qs = CNCProcess.objects.filter(route_id=routeId).order_by('seqnum').prefetch_related('work_steps__step')
    return qs


@router.post('/cnc_route', response=CNCRouteCreateOut, url_name='c_gongyi/cnc_route/create')
def create_cnc_route(request, payload: CNCRouteCreateIn):
    """创建CNC工艺路线，包括Route和多个CNCProcess"""
    if not payload.cnc_processes:
        return {'route_id': 0, 'route_text': '', 'message': '缺少CNC工序数据'}

    # 获取BomVersion
    bom_ver_obj = BomVersion.objects.filter(material_id=payload.material_id, version=payload.version).first()
    if not bom_ver_obj:
        return {'route_id': 0, 'route_text': '', 'message': '物料版本不存在'}

    # 获取订单信息
    order_obj = Order.objects.filter(order_id=payload.order_id).first()
    if not order_obj:
        return {'route_id': 0, 'route_text': '', 'message': '订单不存在'}

    # 检查是否已存在相同的CNC工艺路线
    existing_route = _check_exist_cnc_route(payload)
    if existing_route:
        return {
            'route_id': existing_route.id,
            'route_text': '',
            'message': f'CNC工艺路线 {existing_route.bom_ver}-V{existing_route.route_ver} 已存在'
        }

    # 验证工序ID是否存在
    all_step_ids = set()
    for cnc_process_data in payload.cnc_processes:
        if 'steps_step_ids' in cnc_process_data:
            all_step_ids.update(cnc_process_data.get('steps_step_ids', []))
    if all_step_ids and Step.objects.filter(id__in=[int(sid) for sid in all_step_ids]).count() != len(all_step_ids):
        return {'route_id': 0, 'route_text': '', 'message': '部分工序不存在'}

    route_obj = None
    try:
        with transaction.atomic():
            # 创建Route
            last_route_ver = Route.objects.filter(bom_ver__material_id=payload.material_id, is_cnc=True)\
                .values_list('route_ver', flat=True).order_by('-route_ver').first()
            route_ver = str(int(last_route_ver) + 1) if last_route_ver else '1'

            route_obj = Route.objects.create(
                bom_ver=bom_ver_obj, route_ver=route_ver, is_cnc=True, product_id=payload.product_id or order_obj.product_id,
                approval_status='draft')

            # 创建CNCProcess
            cnc_process_objs = []
            for cnc_process_data in payload.cnc_processes:
                cnc_proc = CNCProcess.objects.create(
                    route=route_obj,
                    seqnum=cnc_process_data.get('seqnum', 1),
                    params=cnc_process_data.get('params', {}),
                    description=cnc_process_data.get('description', '')
                )
                cnc_process_objs.append(cnc_proc)

            # 创建CNCCraft关系
            craft_relations = []
            for cnc_process_data, cnc_process_obj in zip(payload.cnc_processes, cnc_process_objs):
                steps_step_ids = cnc_process_data.get('steps_step_ids', [])
                steps_parms = cnc_process_data.get('steps_parms', [])

                for step_num, (step_id, parm) in enumerate(zip(steps_step_ids, steps_parms), 1):
                    craft_relations.append(CNCCraft(
                        process=cnc_process_obj,
                        step_num=step_num,
                        step_id=step_id,
                        params=parm if parm else {}
                    ))

            if craft_relations:
                CNCCraft.objects.bulk_create(craft_relations)

    except Exception as e:
        if route_obj:
            route_obj.delete()
        return {'route_id': 0, 'route_text': '', 'message': f'创建失败: {str(e)}'}

    route_text = f"CNC工艺{route_obj.bom_ver}-V{route_obj.route_ver}"
    return {
        'route_id': route_obj.id,
        'route_text': route_text,
        'message': 'CNC工艺路线创建成功'
    }
