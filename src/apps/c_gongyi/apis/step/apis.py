from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.c_gongyi.models import *
from apps.c_gongyi.apis.step.schemas import *

router = Router(tags=['step'])


@router.post('/step', response=StepOut, url_name='c_gongyi/step/create')
def create(request, payload: StepIn):
    item = Step.objects.create(**payload.dict())
    return item


@router.get('/step/{item_id}', response=StepOut, url_name='c_gongyi/step/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(Step, id=item_id)
    return item


@router.get('/step', response=List[StepOut], url_name='c_gongyi/step/list')
@paginate
def list_items(request):
    qs = Step.objects.all()
    return qs


@router.put('/step/{item_id}', response=StepOut, url_name='c_gongyi/step/update')
def update(request, item_id, payload: StepIn):
    item = get_object_or_404(Step, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/step/{item_id}', response=StepOut, url_name='c_gongyi/step/partial_update')
def partial_update(request, item_id, payload: StepIn):
    item = get_object_or_404(Step, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/step/{item_id}', url_name='c_gongyi/step/destroy')
def destroy(request, item_id):
    item = get_object_or_404(Step, id=item_id)
    item.delete()
    return responses.ok('已删除')