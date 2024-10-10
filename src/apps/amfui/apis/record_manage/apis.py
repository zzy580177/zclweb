from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.amfui.models import *
from apps.amfui.apis.record_manage.schemas import *

router = Router(tags=['record_manage'])


@router.post('/record_manage', response=RecordManageOut, url_name='amfui/record_manage/create')
def create(request, payload: RecordManageIn):
    item = RecordManage.objects.create(**payload.dict())
    return item


@router.get('/record_manage/{item_id}', response=RecordManageOut, url_name='amfui/record_manage/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(RecordManage, id=item_id)
    return item


@router.get('/record_manage', response=List[RecordManageOut], url_name='amfui/record_manage/list')
@paginate
def list_items(request):
    qs = RecordManage.objects.all()
    return qs


@router.put('/record_manage/{item_id}', response=RecordManageOut, url_name='amfui/record_manage/update')
def update(request, item_id, payload: RecordManageIn):
    item = get_object_or_404(RecordManage, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/record_manage/{item_id}', response=RecordManageOut, url_name='amfui/record_manage/partial_update')
def partial_update(request, item_id, payload: RecordManageIn):
    item = get_object_or_404(RecordManage, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/record_manage/{item_id}', url_name='amfui/record_manage/destroy')
def destroy(request, item_id):
    item = get_object_or_404(RecordManage, id=item_id)
    item.delete()
    return responses.ok('已删除')