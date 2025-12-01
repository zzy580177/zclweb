from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.c_gongyi.models import *
from apps.c_gongyi.apis.cnc_craft.schemas import *

router = Router(tags=['cnc_craft'])


@router.post('/cnc_craft', response=CNCCraftOut, url_name='c_gongyi/cnc_craft/create')
def create(request, payload: CNCCraftIn):
    item = CNCCraft.objects.create(**payload.dict())
    return item


@router.get('/cnc_craft/{item_id}', response=CNCCraftOut, url_name='c_gongyi/cnc_craft/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(CNCCraft, id=item_id)
    return item


@router.get('/cnc_craft', response=List[CNCCraftOut], url_name='c_gongyi/cnc_craft/list')
@paginate
def list_items(request):
    qs = CNCCraft.objects.all()
    return qs


@router.put('/cnc_craft/{item_id}', response=CNCCraftOut, url_name='c_gongyi/cnc_craft/update')
def update(request, item_id, payload: CNCCraftIn):
    item = get_object_or_404(CNCCraft, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/cnc_craft/{item_id}', response=CNCCraftOut, url_name='c_gongyi/cnc_craft/partial_update')
def partial_update(request, item_id, payload: CNCCraftIn):
    item = get_object_or_404(CNCCraft, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/cnc_craft/{item_id}', url_name='c_gongyi/cnc_craft/destroy')
def destroy(request, item_id):
    item = get_object_or_404(CNCCraft, id=item_id)
    item.delete()
    return responses.ok('已删除')