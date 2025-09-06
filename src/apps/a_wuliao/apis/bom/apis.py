from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.a_wuliao.models import *
from apps.a_wuliao.apis.bom.schemas import *

router = Router(tags=['bom'])


@router.post('/bom', response=BomOut, url_name='a_wuliao/bom/create')
def create(request, payload: BomIn):
    item = Bom.objects.create(**payload.dict())
    return item


@router.get('/bom/{item_id}', response=BomOut, url_name='a_wuliao/bom/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(Bom, id=item_id)
    return item


@router.get('/bom', response=List[BomOut], url_name='a_wuliao/bom/list')
@paginate
def list_items(request):
    qs = Bom.objects.all()
    return qs


@router.put('/bom/{item_id}', response=BomOut, url_name='a_wuliao/bom/update')
def update(request, item_id, payload: BomIn):
    item = get_object_or_404(Bom, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/bom/{item_id}', response=BomOut, url_name='a_wuliao/bom/partial_update')
def partial_update(request, item_id, payload: BomIn):
    item = get_object_or_404(Bom, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/bom/{item_id}', url_name='a_wuliao/bom/destroy')
def destroy(request, item_id):
    item = get_object_or_404(Bom, id=item_id)
    item.delete()
    return responses.ok('已删除')