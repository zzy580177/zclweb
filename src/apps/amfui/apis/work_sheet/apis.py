from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.amfui.models import *
from apps.amfui.apis.work_sheet.schemas import *

router = Router(tags=['work_sheet'])


@router.post('/work_sheet', response=WorkSheetOut, url_name='amfui/work_sheet/create')
def create(request, payload: WorkSheetIn):
    item = WorkSheet.objects.create(**payload.dict())
    return item


@router.get('/work_sheet/{item_id}', response=WorkSheetOut, url_name='amfui/work_sheet/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(WorkSheet, id=item_id)
    return item


@router.get('/work_sheet', response=List[WorkSheetOut], url_name='amfui/work_sheet/list')
@paginate
def list_items(request):
    qs = WorkSheet.objects.all()
    return qs


@router.put('/work_sheet/{item_id}', response=WorkSheetOut, url_name='amfui/work_sheet/update')
def update(request, item_id, payload: WorkSheetIn):
    item = get_object_or_404(WorkSheet, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/work_sheet/{item_id}', response=WorkSheetOut, url_name='amfui/work_sheet/partial_update')
def partial_update(request, item_id, payload: WorkSheetIn):
    item = get_object_or_404(WorkSheet, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/work_sheet/{item_id}', url_name='amfui/work_sheet/destroy')
def destroy(request, item_id):
    item = get_object_or_404(WorkSheet, id=item_id)
    item.delete()
    return responses.ok('已删除')