from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses
from apps.bmui.models  import Material

from apps.pmcui.models import ProcessStepSteps  # 显式导入模型
from apps.pmcui.apis.process_step_steps.schemas import *
from django.db.models import F,  Q,  Subquery, OuterRef
from django.db.models.functions import Coalesce 

router = Router(tags=['process_step_steps'])


@router.post('/process_step_steps', response=ProcessStepStepsOut, url_name='pmcui/process_step_steps/create')
def create(request, payload: ProcessStepStepsIn):
    item = ProcessStepSteps.objects.create(**payload.dict())
    return item


@router.get('/process_step_steps/{item_id}', response=ProcessStepStepsOut, url_name='pmcui/process_step_steps/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(ProcessStepSteps, id=item_id)
    return item


@router.get('/process_step_steps', response=List[ProcessStepStepsOut], url_name='pmcui/process_step_steps/list')
@paginate
def list_items(request):
    qs = ProcessStepSteps.objects.select_related('processstep', 'step') 
    #qs = qs.order_by('Route_id', 'subRoute_id', 'SeqNum')
    return qs


@router.put('/process_step_steps/{item_id}', response=ProcessStepStepsOut, url_name='pmcui/process_step_steps/update')
def update(request, item_id, payload: ProcessStepStepsIn):
    item = get_object_or_404(ProcessStepSteps, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/process_step_steps/{item_id}', response=ProcessStepStepsOut, url_name='pmcui/process_step_steps/partial_update')
def partial_update(request, item_id, payload: ProcessStepStepsIn):
    item = get_object_or_404(ProcessStepSteps, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/process_step_steps/{item_id}', url_name='pmcui/process_step_steps/destroy')
def destroy(request, item_id):
    item = get_object_or_404(ProcessStepSteps, id=item_id)
    item.delete()
    return responses.ok('已删除')

@router.get('/route_subMaterial/{item_id}', response=List[RouteSubMaterialOut], url_name='pmcui/process_step_steps/route_subMaterial')
def route_subMaterial(request, item_id):
    qs = ProcessStepSteps.objects.select_related('processstep', 'step__EqpType')  # 添加EqpType预取
    qs = qs.filter(
        Q(processstep__Route_id=item_id) & Q(step__EqpType__Name='中间件')
    ).annotate(
        FId=Coalesce(Subquery(
            Material.objects.filter(FModel=OuterRef('parameters')).values('FId')[:1]),None),
        FNumber=Coalesce(Subquery(
            Material.objects.filter(FModel=OuterRef('parameters')).values('FNumber')[:1]),None),
        FName=Coalesce(Subquery(
            Material.objects.filter(FModel=OuterRef('parameters')).values('FName')[:1]),None),
        FModel=F('parameters')).values('FId', 'FNumber', 'FName','FModel','parameters').distinct()
    return qs