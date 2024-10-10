from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.amfui.models import *
from apps.amfui.apis.record.schemas import *

router = Router(tags=['record'])


@router.post('/record', response=RecordOut, url_name='amfui/record/create')
def create(request, payload: RecordIn):
    item = Record.objects.create(**payload.dict())
    return item


@router.get('/record/{item_id}', response=RecordOut, url_name='amfui/record/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(Record, id=item_id)
    return item


@router.get('/record', response=List[RecordOut], url_name='amfui/record/list')
@paginate
def list_items(request):
    qs = Record.objects.all()
    return qs


@router.put('/record/{item_id}', response=RecordOut, url_name='amfui/record/update')
def update(request, item_id, payload: RecordIn):
    item = get_object_or_404(Record, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/record/{item_id}', response=RecordOut, url_name='amfui/record/partial_update')
def partial_update(request, item_id, payload: RecordIn):
    item = get_object_or_404(Record, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/record/{item_id}', url_name='amfui/record/destroy')
def destroy(request, item_id):
    item = get_object_or_404(Record, id=item_id)
    item.delete()
    return responses.ok('已删除')