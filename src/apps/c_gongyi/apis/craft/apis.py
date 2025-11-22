from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.c_gongyi.models import *
from apps.c_gongyi.apis.craft.schemas import *

router = Router(tags=['craft'])


@router.post('/craft', response=CraftOut, url_name='c_gongyi/craft/create')
def create(request, payload: CraftIn):
    item = Craft.objects.create(**payload.dict())
    return item


@router.get('/craft/{item_id}', response=CraftOut, url_name='c_gongyi/craft/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(Craft, id=item_id)
    return item


@router.get('/craft', response=List[CraftOut], url_name='c_gongyi/craft/list')
@paginate
def list_items(request):
    qs = Craft.objects.all()
    return qs


@router.put('/craft/{item_id}', response=CraftOut, url_name='c_gongyi/craft/update')
def update(request, item_id, payload: CraftIn):
    item = get_object_or_404(Craft, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/craft/{item_id}', response=CraftOut, url_name='c_gongyi/craft/partial_update')
def partial_update(request, item_id, payload: CraftIn):
    item = get_object_or_404(Craft, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/craft/{item_id}', url_name='c_gongyi/craft/destroy')
def destroy(request, item_id):
    item = get_object_or_404(Craft, id=item_id)
    item.delete()
    return responses.ok('已删除')