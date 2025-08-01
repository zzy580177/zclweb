from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.amfui.models import *
from apps.amfui.apis.work_sheet.schemas import *

from django.db.models import Sum, F, Value, IntegerField

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

@router.get('/record', response=List[WorkSheetRecordOut], url_name='amfui/work_sheet/record')
def worksheet_records(request):
    qs1 = Record.objects.select_related('WorkSheet').annotate(
        worksheet_id=F('WorkSheet__Id')
    ).values('worksheet_id').annotate(
        finish_parts=Sum('FinishParts'),
        idle_sec=Sum('IdleTMSec'),
        power_on_sec=Sum('PowerOnSec'),
        working_sec=Sum('WorkingSec'),
        estimated_sec=Sum('EstimatedSec')
    )
    qs2 = WorkSheet.objects.all().annotate(
        req_parts=F('ReqParts') + F('AddReqParts'),
        idle_sec=Value(0, output_field=IntegerField()),
        power_on_sec=Value(0, output_field=IntegerField()),
        working_sec=Value(0, output_field=IntegerField()),
        estimated_sec=Value(0, output_field=IntegerField())
    )
    
    # 合并两个QuerySet并更新
    from django.db import transaction
    with transaction.atomic():
        for record in qs1:
            worksheet = qs2.get(Id=record['worksheet_id'])
            worksheet.FinishParts = record['finish_parts']
            worksheet.idle_sec = record['idle_sec']
            worksheet.power_on_sec = record['power_on_sec']
            worksheet.working_sec = record['working_sec']
            worksheet.estimated_sec = record['estimated_sec']
            worksheet.save()
    return qs2