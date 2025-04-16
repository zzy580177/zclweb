from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.bmui.models import *
from apps.bmui.apis.bom_level.schemas import *

router = Router(tags=['bom_level'])


@router.post('/bom_level', response=BOMLevelOut, url_name='bmui/bom_level/create')
def create(request, payload: BOMLevelIn):
    item = BOMLevel.objects.create(**payload.dict())
    return item


@router.get('/bom_level/{item_id}', response=BOMLevelOut, url_name='bmui/bom_level/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(BOMLevel, id=item_id)
    return item


@router.get('/bom_level', response=List[BOMLevelOut], url_name='bmui/bom_level/list')
@paginate
def list_items(request):
    qs = BOMLevel.objects.all()
    return qs


@router.put('/bom_level/{item_id}', response=BOMLevelOut, url_name='bmui/bom_level/update')
def update(request, item_id, payload: BOMLevelIn):
    item = get_object_or_404(BOMLevel, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/bom_level/{item_id}', response=BOMLevelOut, url_name='bmui/bom_level/partial_update')
def partial_update(request, item_id, payload: BOMLevelIn):
    item = get_object_or_404(BOMLevel, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/bom_level/{item_id}', url_name='bmui/bom_level/destroy')
def destroy(request, item_id):
    item = get_object_or_404(BOMLevel, id=item_id)
    item.delete()
    return responses.ok('已删除')