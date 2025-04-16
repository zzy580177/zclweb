from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.bmui.models import *
from apps.bmui.apis.material.schemas import *

router = Router(tags=['material'])


@router.post('/material', response=MaterialOut, url_name='bmui/material/create')
def create(request, payload: MaterialIn):
    item = Material.objects.create(**payload.dict())
    return item


@router.get('/material/{item_id}', response=MaterialOut, url_name='bmui/material/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(Material, id=item_id)
    return item


@router.get('/material', response=List[MaterialOut], url_name='bmui/material/list')
@paginate
def list_items(request):
    qs = Material.objects.all()
    return qs


@router.put('/material/{item_id}', response=MaterialOut, url_name='bmui/material/update')
def update(request, item_id, payload: MaterialIn):
    item = get_object_or_404(Material, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/material/{item_id}', response=MaterialOut, url_name='bmui/material/partial_update')
def partial_update(request, item_id, payload: MaterialIn):
    item = get_object_or_404(Material, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/material/{item_id}', url_name='bmui/material/destroy')
def destroy(request, item_id):
    item = get_object_or_404(Material, id=item_id)
    item.delete()
    return responses.ok('已删除')