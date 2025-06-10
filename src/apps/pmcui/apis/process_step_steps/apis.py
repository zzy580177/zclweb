from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.pmcui.models import *
from apps.pmcui.apis.process_step_steps.schemas import *

router = Router(tags=['process_step_steps'])


@router.post('/process_step_steps', response=ProcessStepStepsOut, url_name='pmcui/process_step_steps/create')
def create(request, payload: ProcessStepStepsIn):
    item = ProcessStep.objects.create(**payload.dict())
    return item


@router.get('/process_step_steps/{item_id}', response=ProcessStepStepsOut, url_name='pmcui/process_step_steps/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(ProcessStep, id=item_id)
    return item


@router.get('/process_step_steps', response=List[ProcessStepStepsOut], url_name='pmcui/process_step_steps/list')
@paginate
def list_items(request):
    qs = ProcessStep.objects.select_related('Route','subRoute') 
    qs = qs.order_by('route__id', 'subroute__id', 'seq_num')
    return qs


@router.put('/process_step_steps/{item_id}', response=ProcessStepStepsOut, url_name='pmcui/process_step_steps/update')
def update(request, item_id, payload: ProcessStepStepsIn):
    item = get_object_or_404(ProcessStep, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/process_step_steps/{item_id}', response=ProcessStepStepsOut, url_name='pmcui/process_step_steps/partial_update')
def partial_update(request, item_id, payload: ProcessStepStepsIn):
    item = get_object_or_404(ProcessStep, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/process_step_steps/{item_id}', url_name='pmcui/process_step_steps/destroy')
def destroy(request, item_id):
    item = get_object_or_404(ProcessStep, id=item_id)
    item.delete()
    return responses.ok('已删除')