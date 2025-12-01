from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.c_gongyi.models import *
from apps.c_gongyi.apis.cnc_process.schemas import *

router = Router(tags=['cnc_process'])


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