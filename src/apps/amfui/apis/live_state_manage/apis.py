from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router

from apps.amfui.models import *
from apps.amfui.apis.live_state_manage.schemas import *
from datetime import datetime, timedelta
from django.db.models import Sum, Q, Count, F, Max, Value, CharField,Case, When,Avg, IntegerField
from django.db.models.functions import Cast, Concat, ExtractMonth, ExtractDay, ExtractHour, ExtractMinute
import copy

router = Router(tags=['live_state_manage'])


@router.get("/live_state_manage/cellcnt",  url_name='amfui/live_state_manage/cellcnt')
def get_cell_cnt(request):
    return Cell.objects.all().count()

@router.get("/live_state_manage/cellstatus",  url_name='amfui/live_state_manage/cellstatus')
def get_cellstatus(request):
    qs = Stato.objects.values('Cell_id').annotate(last_id=Max('id')).values('last_id')
    qs = Stato.objects.filter(id__in=qs).annotate(
        combined_string=Concat(
            Cast(ExtractMonth('DataTime'), CharField()), Value('-'), Cast(ExtractDay('DataTime'), CharField()), Value(' '),
            Cast(ExtractHour('DataTime'), CharField()), Value(':'), Cast(ExtractMinute('DataTime'), CharField()), Value(' | '),
            'Cell__Name', Value('-'), Cast('Cell__CellID', CharField()))
    ).values('combined_string','Alarmi__AlarmString', 'Stato')
    result = list(qs)
    qs=None
    return result

