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


def _check_exist_route(payload: List[ProcessIn]):
    routes = Route.objects.filter(bom_ver__material_id=payload[0].material_id).prefetch_related(
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
            lastRouteVer = Route.objects.filter(bom_ver__material_id=payload[0].material_id).values_list('route_ver', flat=True).order_by('-route_ver').first()
            route_ver = str(int(lastRouteVer) + 1) if lastRouteVer else '1'
            route_obj = Route.objects.create(bom_ver=bomVer_obj, route_ver=route_ver, is_cnc=False, 
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
