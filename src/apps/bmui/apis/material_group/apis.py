from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.bmui.models import *
from apps.bmui.apis.material_group.schemas import *

router = Router(tags=['material_group'])


@router.post('/material_group', response=MaterialGroupOut, url_name='bmui/material_group/create')
def create(request, payload: MaterialGroupIn):
    item = MaterialGroup.objects.create(**payload.dict())
    return item


@router.get('/material_group/{item_id}', response=MaterialGroupOut, url_name='bmui/material_group/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(MaterialGroup, id=item_id)
    return item


@router.get('/material_group', response=List[MaterialGroupOut], url_name='bmui/material_group/list')
@paginate
def list_items(request):
    qs = MaterialGroup.objects.all()
    return qs


@router.put('/material_group/{item_id}', response=MaterialGroupOut, url_name='bmui/material_group/update')
def update(request, item_id, payload: MaterialGroupIn):
    item = get_object_or_404(MaterialGroup, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/material_group/{item_id}', response=MaterialGroupOut, url_name='bmui/material_group/partial_update')
def partial_update(request, item_id, payload: MaterialGroupIn):
    item = get_object_or_404(MaterialGroup, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/material_group/{item_id}', url_name='bmui/material_group/destroy')
def destroy(request, item_id):
    item = get_object_or_404(MaterialGroup, id=item_id)
    item.delete()
    return responses.ok('已删除')