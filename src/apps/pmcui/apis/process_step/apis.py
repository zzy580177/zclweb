from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.pmcui.models import *
from apps.pmcui.apis.process_step.schemas import *
from apps.bmui.models import Material
from django.db.models import Sum, F, Q, Prefetch, IntegerField, Subquery, Case, CharField, OuterRef, When, Avg, FloatField
from django.db.models.functions import Concat, TruncDate, Coalesce 
from django.db import transaction

router = Router(tags=['process_step'])


@router.post('/process_step', response=list[ProcessStepSampleOut], url_name='pmcui/process_step/create')
def create(request, payload: list[ProcessStepSampleIn]):
    item = ProcessStep.objects.create(**payload.dict())
    return item


@router.get('/process_step/{item_id}', response=ProcessStepOut, url_name='pmcui/process_step/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(ProcessStep, id=item_id)
    return item


@router.get('/process_step', response=List[ProcessStepOut], url_name='pmcui/process_step/list')
@paginate
def list_items(request):
    qs = ProcessStep.objects.select_related('Route','subRoute').prefetch_related('Steps') 
    qs = qs.order_by('Route_id', 'subRoute_id', 'SeqNum')
    return qs


@router.put('/process_step/{item_id}', response=ProcessStepOut, url_name='pmcui/process_step/update')
def update(request, item_id, payload: ProcessStepIn):
    item = get_object_or_404(ProcessStep, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/process_step/{item_id}', response=ProcessStepOut, url_name='pmcui/process_step/partial_update')
def partial_update(request, item_id, payload: ProcessStepIn):
    item = get_object_or_404(ProcessStep, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/process_step/{item_id}', url_name='pmcui/process_step/destroy')
def destroy(request, item_id):
    item = get_object_or_404(ProcessStep, id=item_id)
    item.delete()
    return responses.ok('已删除')

@router.get('/router_processes/{item_id}', response=list[ProcessStepSampleOut], url_name='pmcui/process_step/router_processes')
def router_processes(request, item_id):
    qs = ProcessStep.objects.select_related('subRoute','Route__Material').prefetch_related('Steps')
    qs = qs.filter(Route_id = item_id).annotate(FId =F('Route__Material_id'),FName = F('Route__Material__FName'),
        FModel = F('Route__Material__FModel'), FNumber = F('Route__Material__FNumber')).order_by('SeqNum')
    return qs

def _check_exist_route(payload: List[ProcessStepSampleIn]):
    routes = ProcessRoute.objects.filter(Material_id=payload[0].FId).prefetch_related(Prefetch('main_steps', 
        queryset=ProcessStep.objects.prefetch_related('Steps').annotate(FId =F('Route__Material_id'),FName = F('Route__Material__FName'),
        FModel = F('Route__Material__FModel'), FNumber = F('Route__Material__FNumber')).order_by('SeqNum')))
    for route in routes:
        main_steps = list(route.main_steps.all())
        if len(main_steps) != len(payload):
            continue
        qs_steps = [ProcessStepSampleOut.from_orm(step) for step in main_steps]
        if all(
            qs_step.Steps_Step_Id == payload_step.Steps_Step_Id and
            qs_step.Process_Steps_Parm == payload_step.Process_Steps_Parm
            for qs_step, payload_step in zip(qs_steps, payload)):
            return route.Id
    return None

@router.post('/check_update',  url_name='pmcui/process_step/check_update')
def check_update(request, payload: list[ProcessStepSampleIn]):
    result = _check_exist_route(payload)
    if result:
        return {'success':True, 'data':{'routeId': result, 'message': f'已存在可匹配工艺线路-{result}'}}
    part_obj = get_object_or_404(Material, FId=payload[0].FId)
    if not part_obj:
        return {'success':False,'data':{'message': f'物料-ID:{payload[0].FId} Name:{payload[0].FName} 已丢失'}}
    route_obj = None;
    process_objs = None;
    step_objs = None;
    try:
        with transaction.atomic():
            route_obj = ProcessRoute.objects.create(Material_id=part_obj.FId, ApprovalStatus="未就緒")
            process_objs = []
            for process in payload:
                step = ProcessStep(Route=route_obj, SeqNum=process.SeqNum, Description=process.Description)
                step.save()
                process_objs.append(step)
            step_relations = []
            for process, process_obj in zip(payload, process_objs):
                step_relations.extend([
                    ProcessStepSteps(processstep=process_obj, step_id=step_id, parameters=parm if parm else ''
                    ) for step_id, parm in zip(process.Steps_Step_Id, process.Process_Steps_Parm)])
            
            step_objs = ProcessStepSteps.objects.bulk_create(step_relations)

    except Exception as e:
        if step_objs:
            ProcessStepSteps.objects.filter(processstep__Route=route_obj).delete()
        if process_objs:
            ProcessStep.objects.filter(Route=route_obj).delete()
        if route_obj:
            route_obj.delete()
        return {'success':False, 'data':{'message': f'创建失败: {str(e)}'}}
    return {'success':True, 'data':{'routeId': route_obj.Id, 'message': f'工艺路线创建成功'}}

