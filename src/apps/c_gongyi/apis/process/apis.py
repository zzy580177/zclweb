from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate
from ninja.security import django_auth
from django.db import transaction
from django.db.models import F, Prefetch,Q
from django_starter.db.base_models import *

from django_starter.http.response import responses


from apps.c_gongyi.models import *
from apps.c_gongyi.apis.process.schemas import *
from apps.a_wuliao.models import *
from apps.b_jihua.models import *

router = Router(tags=['process'])

def _check_exist_route_process(payload: RouteCreateIn):

    try:
        routes = Route.objects.filter(bom_ver__material_id=payload.material_id, is_cnc=payload.is_cnc).prefetch_related(
            Prefetch('processes', queryset=Process.objects.order_by('seqnum')))
        for route in routes:
            processes = list(route.processes.all().order_by('seqnum'))
            if len(processes) != len(payload.processes):
                continue

            all_match = True
            for qs_process, payload_process in zip(processes, payload.processes):
                # 获取工序的详细步骤信息
                crafts = Craft.objects.filter(process=qs_process).order_by('step_num', 'id')
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
    except Exception as e:
        return None

    return None


@router.post('/route', response=RouteCreateOut, url_name='c_gongyi/route/create')
def create_route(request, payload: RouteCreateIn):
    """创建CNC工艺路线，包括Route和多个CNCProcess"""
    if not payload.processes:
        return {'success': False, 'data': {},  'message': '缺少CNC工序数据' if payload.is_cnc else '缺少工序数据'}

    bom_ver_obj = BomVersion.objects.filter(material_id=payload.material_id, version=payload.version).first()
    if not bom_ver_obj:
        return {'success': False, 'data': {},  'message': '物料版本不存在'}

    order_obj = Order.objects.filter(order_id=payload.order_id).first()
    if not order_obj:
        return {'success': False, 'data': {}, 'message': '订单不存在'}

    existing_route = _check_exist_route_process(payload)

    if existing_route:
        text = f"工艺: CNC{existing_route.bom_ver}-V{existing_route.route_ver}" if payload.is_cnc else f"工艺: {existing_route.bom_ver}-V{existing_route.route_ver}",
        return {'success': True,  
                'data': {'id': existing_route.id, 'text': f'工艺{existing_route.bom_ver}-V{existing_route.route_ver}'}, 
                'message':  f'{text}已存在'}

    # 验证工序ID是否存在
    all_step_ids = set()
    for process_data in payload.processes:
        if 'steps_step_ids' in process_data:
            all_step_ids.update(process_data.get('steps_step_ids', []))
    if all_step_ids and Step.objects.filter(id__in=[int(sid) for sid in all_step_ids]).count() != len(all_step_ids):
        return {'success': False, 'data': {},  'message': '部分工序不存在'}

    route_obj = None
    try:
        with transaction.atomic():
            # 创建Route
            last_route_ver = Route.objects.filter(bom_ver__material_id=payload.material_id, is_cnc=payload.is_cnc)\
                .values_list('route_ver', flat=True).order_by('-route_ver').first()
            route_ver = str(int(last_route_ver) + 1) if last_route_ver else '1'

            route_obj = Route.objects.create(
                bom_ver=bom_ver_obj, route_ver=route_ver, is_cnc=payload.is_cnc, product_id=payload.product_id or order_obj.product_id,approval_status='draft')
            process_objs = []
            for process_data in payload.processes:
                proc = Process.objects.create(
                    route=route_obj, seqnum=process_data.get('seqnum', 1), params=process_data.get('params', {}), description=process_data.get('description', ''))
                process_objs.append(proc)

            # 创建CNCCraft关系
            craft_relations = []
            for process_data, process_obj in zip(payload.processes, process_objs):
                steps_step_ids = process_data.get('steps_step_ids', [])
                steps_parms = process_data.get('steps_parms', [])

                for step_num, (step_id, parm) in enumerate(zip(steps_step_ids, steps_parms), 1):
                    craft_relations.append(Craft(
                        process=process_obj, step_num=step_num, step_id=step_id, params=parm if parm else {}))

            if craft_relations:
                Craft.objects.bulk_create(craft_relations)

    except Exception as e:
        if route_obj:
            route_obj.delete()
        return {'success': False, 'data': {}, 'message': f'创建失败: {str(e)}'}

    route_text = f"CNC工艺 {route_obj.bom_ver}-V{route_obj.route_ver}" if payload.is_cnc else f"工艺 {route_obj.bom_ver}-V{route_obj.route_ver}"
    return {
        'success': True,
        'data': {'id': route_obj.id, 'text': f"工艺{route_obj.bom_ver}-V{route_obj.route_ver}"},
        'message': f'{route_text}创建成功'
    }

@router.put('/route/{item_id}', response=RouteCreateOut, url_name='c_gongyi/route/update')
def update_route(request, item_id, payload: RouteCreateIn):
    route_obj = get_object_or_404(Route, id=item_id)

    if route_obj.bom_ver.material_id != payload.material_id:
        return {'success': False, 'data': {},  'message': '物料不匹配'}

    if route_obj.is_cnc != payload.is_cnc:
        return {'success': False, 'data': {},  'message': '工艺类型不匹配'}

    if not payload.processes:
        return {'success': False, 'data': {},  'message': '缺少CNC工序数据' if payload.is_cnc else '缺少工序数据'}

    bom_ver_obj = BomVersion.objects.filter(material_id=payload.material_id, version=payload.version).first()
    if bom_ver_obj != route_obj.bom_ver:
        return {'success': False, 'data': {},  'message': '物料版本不匹配'}

    all_step_ids = set()
    for process_data in payload.processes:
        if 'steps_step_ids' in process_data:
            all_step_ids.update(process_data.get('steps_step_ids', []))
    if all_step_ids and Step.objects.filter(id__in=[int(sid) for sid in all_step_ids]).count() != len(all_step_ids):
        return {'success': False, 'data': {}, 'message': '部分工序不存在'}

    try:
        with transaction.atomic():
            # 删除旧的工序和工艺配方
            old_processes = Process.objects.filter(Q(route_id=item_id) | Q(subroute_id=item_id))
            for proc in old_processes:
                proc.steps.clear()  # 清除多对多关系
            old_processes.delete()  # 删除工序，会级联删除工艺配方

            # 创建新的工序
            process_objs = []
            for process_data in payload.processes:
                proc = Process.objects.create(
                    route=route_obj, seqnum=process_data.get('seqnum', 1), params=process_data.get('params', {}), description=process_data.get('description', ''))
                process_objs.append(proc)

            # 创建CNCCraft关系
            craft_relations = []
            for process_data, process_obj in zip(payload.processes, process_objs):
                steps_step_ids = process_data.get('steps_step_ids', [])
                steps_parms = process_data.get('steps_parms', [])

                for step_num, (step_id, parm) in enumerate(zip(steps_step_ids, steps_parms), 1):
                    craft_relations.append(Craft(
                        process=process_obj, step_num=step_num, step_id=step_id, params=parm if parm else {}))

            if craft_relations:
                Craft.objects.bulk_create(craft_relations)

    except Exception as e:
        return {'success': False, 'data': {}, 'message': f'更新失败: {str(e)}'}

    route_text = f"工艺: CNC{route_obj.bom_ver}-V{route_obj.route_ver}" if payload.is_cnc else f"工艺: {route_obj.bom_ver}-V{route_obj.route_ver}"
    return {
        'success': True,
        'data': {'id': route_obj.id, 'text': f"工艺{route_obj.bom_ver}-V{route_obj.route_ver}"},
        'message': f'{route_text} 更新成功'
    }


def _check_exist_route(payload: List[ProcessIn]):
    routes = Route.objects.filter(bom_ver__material_id=payload[0].material_id, is_cnc = payload[0].isCNC).prefetch_related(
        Prefetch('main_steps',  queryset=Process.objects.prefetch_related('steps').annotate(
            material_id =F('route__bom_ver__material_id')).order_by('seqnum')))
    for route in routes:
        main_steps = list(route.main_steps.all())
        if len(main_steps) != len(payload):
            continue
        for step in main_steps:
            process = ProcessOut.from_orm(step)
            
        qs_steps = [ProcessOut.from_orm(step) for step in main_steps]
        if all(
            qs_step.steps_step_ids == payload_step.steps_step_ids and
            qs_step.steps_parms == payload_step.steps_parms
            for qs_step, payload_step in zip(qs_steps, payload)):
            return route
    return None

@router.post('/process',  url_name='c_gongyi/process/create')
def create(request, payload: List[ProcessIn]):
    if not payload:
        return {'success': False, 'data': {'message': '缺少参数'}}
    if not all(isinstance(item, ProcessIn) for item in payload):
        return {'success': False, 'data': {'message': '参数格式错误'}}
    is_cnc = payload[0].isCNC
    bomVer_obj = BomVersion.objects.filter(material_id=payload[0].material_id, version=payload[0].version).first()
    if not bomVer_obj:
        return {'success': False, 'data': {'message': '物料不存在'}}
    
    # Validate that all step_ids exist
    all_step_ids = set()
    for process in payload:
        all_step_ids.update(process.steps_step_ids or [])
    if all_step_ids and Step.objects.filter(id__in=[int(sid) for sid in all_step_ids]).count() != len(all_step_ids):
        return {'success': False, 'data': {'message': '部分工序不存在'}}
    
    exit_route = _check_exist_route(payload)
    if exit_route:
        return {'success': False, 'data': {'message': f'工艺路线 {exit_route.bom_ver}-V{exit_route.route_ver}已存在'}}

    order_obj = Order.objects.filter(order_id=payload[0].order_id).first()

    route_obj = None
    try:
        with transaction.atomic():
            lastRouteVer = Route.objects.filter(bom_ver__material_id=payload[0].material_id, is_cnc=is_cnc
                ).values_list('route_ver', flat=True).order_by('-route_ver').first()
            route_ver = str(int(lastRouteVer) + 1) if lastRouteVer else '1'
            route_obj = Route.objects.create(bom_ver=bomVer_obj, route_ver=route_ver, is_cnc=is_cnc, 
                                             product_id=order_obj.product_id, approval_status='draft')

            process_objs = []
            for process in payload:
                proc = Process(route=route_obj, seqnum=process.seqnum, description=process.description)
                proc.save()
                process_objs.append(proc)

            step_relations = []
            for process, process_obj in zip(payload, process_objs):
                step_relations.extend([
                    Craft(process=process_obj, step_id=step_id, params=parm if parm else ''
                    ) for step_id, parm in zip(process.steps_step_ids, process.steps_parms)])

            Craft.objects.bulk_create(step_relations)

    except Exception as e:
        if route_obj:
            route_obj.delete()
        return {'success': False, 'data': {'message': f'创建失败, {str(e)}'}}
    return {'success': True, 'data': {'routeId': route_obj.id,'text': f"工艺{route_obj.bom_ver}-V{route_obj.route_ver}", 'message': '工艺路线创建成功'}} 



@router.get('/process/{item_id}', response=ProcessOut, url_name='c_gongyi/process/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(Process, id=item_id)
    return item


@router.get('/route/{item_id}', response=list[ProcessOut], url_name='c_gongyi/process/route')
def route(request, item_id):
    qs = Process.objects.filter(Q(route_id=item_id) | Q(subroute_id=item_id)).order_by('seqnum').prefetch_related('steps')
    return qs

@router.get('/process', response=List[ProcessOut], url_name='c_gongyi/process/list')
@paginate
def list_items(request, material_id: int = None, route_id: int = None,  version: str = None):
    qs = Process.objects.all()
    if material_id:
        qs = qs.filter(route__bom_ver__material_id=material_id)
    if version:
        qs = qs.filter(route__bom_ver__version=version)
    if route_id:
        qs = qs.filter(route_id=route_id)

    return qs.order_by('route_id','seqnum')


@router.put('/process/{item_id}', response=ProcessOut, url_name='c_gongyi/process/update')
def update(request, item_id, payload: ProcessIn):
    item = get_object_or_404(Process, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/process/{item_id}', response=ProcessOut, url_name='c_gongyi/process/partial_update')
def partial_update(request, item_id, payload: ProcessIn):
    item = get_object_or_404(Process, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/process/{item_id}', url_name='c_gongyi/process/destroy')
def destroy(request, item_id):
    item = get_object_or_404(Process, id=item_id)
    item.delete()
    return responses.ok('已删除')
