from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.bmui.models import *
from apps.bmui.apis.bom.schemas import *

router = Router(tags=['bom'])


@router.post('/bom', response=BOMOut, url_name='bmui/bom/create')
def create(request, payload: BOMIn):
    item = BOM.objects.create(**payload.dict())
    return item


@router.get('/bom/{item_id}', response=BOMOut, url_name='bmui/bom/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(BOM, id=item_id)
    return item


@router.get('/bom', response=List[BOMOut], url_name='bmui/bom/list')
@paginate
def list_items(request):
    qs = BOM.objects.all()
    return qs


@router.put('/bom/{item_id}', response=BOMOut, url_name='bmui/bom/update')
def update(request, item_id, payload: BOMIn):
    item = get_object_or_404(BOM, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/bom/{item_id}', response=BOMOut, url_name='bmui/bom/partial_update')
def partial_update(request, item_id, payload: BOMIn):
    item = get_object_or_404(BOM, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/bom/{item_id}', url_name='bmui/bom/destroy')
def destroy(request, item_id):
    item = get_object_or_404(BOM, id=item_id)
    item.delete()
    return responses.ok('已删除')