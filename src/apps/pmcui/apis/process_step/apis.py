from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.pmcui.models import *
from apps.pmcui.apis.process_step.schemas import *

router = Router(tags=['process_step'])


@router.post('/process_step', response=ProcessStepOut, url_name='pmcui/process_step/create')
def create(request, payload: ProcessStepIn):
    item = ProcessStep.objects.create(**payload.dict())
    return item


@router.get('/process_step/{item_id}', response=ProcessStepOut, url_name='pmcui/process_step/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(ProcessStep, id=item_id)
    return item


@router.get('/process_step', response=List[ProcessStepOut], url_name='pmcui/process_step/list')
@paginate
def list_items(request):
    qs = ProcessStep.objects.select_related('Route','subRoute') 
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