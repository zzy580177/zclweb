from typing import List
from itertools import chain
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.amfui.models import *
from apps.amfui.apis.record.schemas import *
from django.db.models import Sum, F, Q, Value, IntegerField, Subquery, Case, CharField, OuterRef, When, Avg, FloatField
from django.db.models.functions import Concat, TruncDate, Coalesce 
from collections import defaultdict
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
    qs = Record.objects.select_related('WorkSheet', 'WorkSheet__Cell').all().annotate(
        date_only=TruncDate('StartTime'),
        cell=F('WorkSheet__Cell')
    )
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

@router.get('/aggregated', response=List[RecordAggregatedOut], url_name='amfui/record/aggregated')
def aggregated_records(request):
    qs = Record.objects.select_related('WorkSheet__Cell').annotate(
		date_only=TruncDate('StartTime'),
		cell_id=F('WorkSheet__Cell')).values('date_only', 'cell_id').annotate(
			cell_str=Concat(
                F('WorkSheet__Cell__Name'), Value(' '), F('WorkSheet__Cell__CellID'),
                output_field=CharField()),
			finish_sum=Coalesce(Sum('FinishParts'), 0, output_field=IntegerField()),
			idle_sum=Coalesce(Sum('IdleTMSec'), 0, output_field=IntegerField()),
			poweron_sum=Coalesce(Sum('PowerOnSec'), 0, output_field=IntegerField()),
			working_sum=Coalesce(
				Sum('WorkingSec', filter=Q(Mode='普通模式')),
				0, output_field=IntegerField()),
			adjust_sum=Coalesce(
				Sum('WorkingSec', filter=Q(Mode='调机模式')),
				0, output_field=IntegerField()),
            
			estimated_sum=Coalesce(Sum('EstimatedSec'), 0, output_field=IntegerField()),
			online_sum=Coalesce(Subquery(LiveState.objects.filter(Check1__date=OuterRef('date_only'), Cell=OuterRef('cell_id')
				).annotate(sum_online=Sum('OnLine')).values('sum_online')[:1], output_field=IntegerField()
				), 0, output_field=IntegerField())).order_by('-date_only')
    return qs
def format_seconds(seconds):
    if seconds is None or seconds == 0:
        return "0"
    seconds = int(seconds)
    days = seconds // (24 * 3600)
    remaining_seconds = seconds % (24 * 3600)
    hours = remaining_seconds // 3600
    minutes = (remaining_seconds % 3600) // 60
    seconds = remaining_seconds % 60
    output = f"{minutes}m {seconds}s"
    if hours>0:
        output = f"{hours}h {minutes}m"
    return output 
stato_choics = ((0, "待机中"), (1, "作业中"), (2, "故障中"), (3, "离线中"))
def getDailyWorkTime(user):
	if user.username == 'yadi':
		return 22
	return 24

@router.get('/daily', url_name='amfui/record/daily')
def daily_records(request, offset=0, itemsPerPage=3):
    cur_date = datetime.now().date()
    dailyTm = getDailyWorkTime(request.user)
    qs = Record.objects.filter(StartTime__date=cur_date).select_related('WorkSheet','WorkSheet__Cell').values('WorkSheet__Cell').annotate(
		cell_name=F('WorkSheet__Cell__Name'),
        cell_id=F('WorkSheet__Cell__CellID'),
        cell_status=Case(
            When(WorkSheet__Cell__Stato=0, then=Value(dict(stato_choics).get(0, '待机中'))),
            When(WorkSheet__Cell__Stato=1, then=Value(dict(stato_choics).get(1, '作业中'))),
            When(WorkSheet__Cell__Stato=2, then=Value(dict(stato_choics).get(2, '故障中'))),
            When(WorkSheet__Cell__Stato=3, then=Value(dict(stato_choics).get(3, '离线中'))),
            default=Value('未知'),
            output_field=CharField()
        ),
        cell_plant=F('WorkSheet__Cell__Plant'),
        cell_alarm=Coalesce(Subquery(Stato.objects.filter(Cell=OuterRef('WorkSheet__Cell')).select_related('Alarmi'
            ).values('Alarmi__AlarmString').order_by('-DataTime')[:1], output_field=CharField()
            ), Value(''), output_field=CharField()),
        worksheet_id=Case(
            When(WorkSheet__Status='加工中', then=F('WorkSheet_id')),
            default=Value(None), output_field=CharField()),
        worksheet_req=Case(
            When(WorkSheet__Status='加工中', then=F('WorkSheet__ReqParts') + F('WorkSheet__AddReqParts')),
            default=Value(None), output_field=IntegerField()),
        worksheet_orderId=Case(
            When(WorkSheet__Status='加工中', then=F('WorkSheet__Order_id')),
            default=Value(None), output_field=CharField()),
        worksheet_productId=Case(
            When(WorkSheet__Status='加工中', then=F('WorkSheet__Product_id')),
            default=Value(None), output_field=CharField()),         
        worksheet_process=Case(
            When(WorkSheet__Status='加工中', then=F('WorkSheet__ProcessID')),
            default=Value(None), output_field=CharField()),       
        worksheet_status=Case(
            When(WorkSheet__Status='加工中', then=F('WorkSheet__Status')),
            default=Value(None), output_field=CharField()),
        worksheet_finish=Coalesce(Subquery(Pezzi.objects.filter(Cell=OuterRef('WorkSheet__Cell'),WorkSheet=OuterRef('worksheet_id')
            ).values('Pezzi').order_by('-DataTime')[:1], output_field=IntegerField()
            ), Value(0), output_field=IntegerField()),
        worksheet_pieceTm=Coalesce(Subquery(Pezzi.objects.filter(
            Cell=OuterRef('WorkSheet__Cell'),WorkSheet=OuterRef('worksheet_id')).exclude(PieceTime=0
        ).annotate(avg_piece_time=Avg('PieceTime')).values('avg_piece_time')[:1], output_field=FloatField()
        ), Value(0.0), output_field=FloatField()),
        worksheet_estimated=Coalesce(Sum('EstimatedSec'), 0, output_field=IntegerField()),
		daily_finish=Coalesce(Sum('FinishParts'), 0, output_field=IntegerField()),
		daily_idle=Coalesce(Sum('IdleTMSec'), 0, output_field=IntegerField()),
		daily_poweron=Coalesce(Sum('PowerOnSec'), 0, output_field=IntegerField()),
		daily_job=Coalesce(Sum('WorkingSec', filter=Q(Mode='普通模式')),
				0, output_field=IntegerField()),
		daily_adjust=Coalesce(Sum('WorkingSec', filter=Q(Mode='调机模式')),
				0, output_field=IntegerField()),	
        daily_tm=Value(dailyTm, output_field=IntegerField()),	
        daily_online=Coalesce(Subquery(LiveState.objects.filter(Check1__date=cur_date, Cell=OuterRef('WorkSheet__Cell')
			).annotate(sum_online=Sum('OnLine')).values('sum_online')[:1], output_field=IntegerField()
			), 0, output_field=IntegerField()))
    for item in qs:
        for key in ['worksheet_pieceTm', 'worksheet_estimated', 'daily_idle', 'daily_poweron', 'daily_job', 'daily_adjust', 'daily_online']:
            if item[key] is not None:
                if key in ['worksheet_pieceTm', 'worksheet_estimated']:
                    item[key] = format_seconds(item[key]/100)
                else:
                    item[key] = format_seconds(item[key])
    result = list(qs)
    result[:] = result[offset:] + result[:offset]
    if itemsPerPage == 0:
        return result
    return result[0:itemsPerPage]