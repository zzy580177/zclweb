from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.amfui.models import *
from apps.amfui.apis.cell.schemas import *

router = Router(tags=['cell'])


@router.post('/cell', response=CellOut, url_name='amfui/cell/create')
def create(request, payload: CellIn):
    item = Cell.objects.create(**payload.dict())
    return item


@router.get('/cell/{item_id}', response=CellOut, url_name='amfui/cell/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(Cell, id=item_id)
    return item


@router.get('/cell', response=List[CellOut], url_name='amfui/cell/list')
@paginate
def list_items(request):
    qs = Cell.objects.all()
    return qs


@router.put('/cell/{item_id}', response=CellOut, url_name='amfui/cell/update')
def update(request, item_id, payload: CellIn):
    item = get_object_or_404(Cell, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/cell/{item_id}', response=CellOut, url_name='amfui/cell/partial_update')
def partial_update(request, item_id, payload: CellIn):
    item = get_object_or_404(Cell, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/cell/{item_id}', url_name='amfui/cell/destroy')
def destroy(request, item_id):
    item = get_object_or_404(Cell, id=item_id)
    item.delete()
    return responses.ok('已删除')