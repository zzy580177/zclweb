from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.fpmui.models import *
from apps.fpmui.apis.process_step.schemas import *

router = Router(tags=['process_step'])


@router.post('/process_step', response=ProcessStepOut, url_name='fpmui/process_step/create')
def create(request, payload: ProcessStepIn):
    item = ProcessStep.objects.create(**payload.dict())
    return item


@router.get('/process_step/{item_id}', response=ProcessStepOut, url_name='fpmui/process_step/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(ProcessStep, id=item_id)
    return item


@router.get('/process_step', response=List[ProcessStepOut], url_name='fpmui/process_step/list')
@paginate
def list_items(request):
    qs = ProcessStep.objects.all()
    return qs


@router.put('/process_step/{item_id}', response=ProcessStepOut, url_name='fpmui/process_step/update')
def update(request, item_id, payload: ProcessStepIn):
    item = get_object_or_404(ProcessStep, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/process_step/{item_id}', response=ProcessStepOut, url_name='fpmui/process_step/partial_update')
def partial_update(request, item_id, payload: ProcessStepIn):
    item = get_object_or_404(ProcessStep, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/process_step/{item_id}', url_name='fpmui/process_step/destroy')
def destroy(request, item_id):
    item = get_object_or_404(ProcessStep, id=item_id)
    item.delete()
    return responses.ok('已删除')