from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.amfui.models import *
from apps.amfui.apis.live_state.schemas import *
from django.db.models.functions import TruncDate, Now
from django.db.models import Sum,F, Value, CharField, Max, BooleanField, ExpressionWrapper
from django.db.models.functions import Concat

router = Router(tags=['live_state'])


@router.post('/live_state', response=LiveStateOut, url_name='amfui/live_state/create')
def create(request, payload: LiveStateIn):
    item = LiveState.objects.create(**payload.dict())
    return item


@router.get('/live_state/{item_id}', response=LiveStateOut, url_name='amfui/live_state/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(LiveState, id=item_id)
    return item


@router.get('/live_state', response=List[LiveStateOut], url_name='amfui/live_state/list')
@paginate
def list_items(request):
    qs = LiveState.objects.all()
    return qs


@router.put('/live_state/{item_id}', response=LiveStateOut, url_name='amfui/live_state/update')
def update(request, item_id, payload: LiveStateIn):
    item = get_object_or_404(LiveState, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/live_state/{item_id}', response=LiveStateOut, url_name='amfui/live_state/partial_update')
def partial_update(request, item_id, payload: LiveStateIn):
    item = get_object_or_404(LiveState, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/live_state/{item_id}', url_name='amfui/live_state/destroy')
def destroy(request, item_id):
    item = get_object_or_404(LiveState, id=item_id)
    item.delete()
    return responses.ok('已删除')

@router.get('/dailylist', response=List[DailyLiveStateOut], url_name='amfui/live_state/dailylist')
@paginate
def list_items(request):
    qs = LiveState.objects.select_related('Cell') \
        .exclude(Cell__Name="ZCL数采平台") \
        .annotate(
            date_only=TruncDate('Check1'),
            cell_str=Concat(F('Cell__Name'), Value(' '), F('Cell__CellID'),
                output_field=CharField())
        ) \
        .values('Cell', 'date_only', 'cell_str') \
        .annotate(online_sec=Sum('OnLine'))
    
    return list(qs)

@router.get('/amflive', response=List[AMFStateOut], url_name='amfui/live_state/amflive')
@paginate
def amflive(request):
    currTm = datetime.now()
    qs = LiveState.objects.select_related('Cell').filter(Cell__Name="ZCL数采平台").annotate(
            cell_str=Concat(F('Cell__Name'), Value(' '), F('Cell__CellID'),output_field=CharField())
        ).values('cell_str').distinct().annotate(
            max_check1=Max('Check1')).order_by('Cell__CellID')
    for item in qs:
        item['isOffLine'] = (currTm - item['max_check1']).total_seconds() > 60 * 5
    return qs