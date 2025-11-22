from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.c_gongyi.models import *
from apps.c_gongyi.apis.process.schemas import *

router = Router(tags=['process'])


@router.post('/process', response=ProcessOut, url_name='c_gongyi/process/create')
def create(request, payload: ProcessIn):
    item = Process.objects.create(**payload.dict())
    return item


@router.get('/process/{item_id}', response=ProcessOut, url_name='c_gongyi/process/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(Process, id=item_id)
    return item


@router.get('/process', response=List[ProcessOut], url_name='c_gongyi/process/list')
@paginate
def list_items(request):
    qs = Process.objects.all()
    return qs


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