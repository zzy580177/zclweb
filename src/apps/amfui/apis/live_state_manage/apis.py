from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.amfui.models import *
from apps.amfui.apis.live_state_manage.schemas import *

from itertools import chain
from datetime import datetime, timedelta
from django.db.models import Sum, Q, Count, CharField, F
from django.db.models.functions import Cast
import copy

router = Router(tags=['live_state_manage'])

defule_CellDic = {
    "Cell_id": "",
    "Cell__Name": "",
    "Cell__CellID": 0,
    "Cell__Plant": "",
    "tot_online": "",
    "tot_adjustTM": "",
    "tot_poweron": "",
    "tot_workTM": "",
    "tot_idleTM": "",
    "tot_parts": "",
    "Cell__Alarmi_id": "",
    "WorkSheet_id": "",
    "WorkSheet__FinishParts": 0,
    "WorkSheet__Status": "",
    "EstimatedSec": "",
    "TotReq": 0,
    "Cell__Alarmi__AllarmString" : "",
    "Cell_get_Alarmi_display" : "",
}
@router.get("/live_state_manage/cell_typeList",  url_name='amfui/live_state_manage/cell_typeList')
def cell_typeList(request):
    metrics = {
         '离线中': Count('id', filter=Q(Alarmi_id='-2')), 
         '待机中': Count('id', filter=Q(Alarmi_id='-1')), 
         '作业中': Count('id', filter=Q(Alarmi_id='0')), 
         '故障中': Count('id', filter= ~(Q(Alarmi_id='-1')|Q(Alarmi_id='-2')|Q(Alarmi_id='0'))),}
    dictL = list(Cell.objects.values('Plant').annotate(**metrics))
    rlist = [{'label':'离线中', 'value': dictL[0]['离线中']},
             {'label':'待机中', 'value':dictL[0]['待机中']},
             {'label':'作业中', 'value':dictL[0]['作业中']},
             {'label':'故障中', 'value':dictL[0]['故障中']}]    
    return rlist
 
@router.get("/live_state_manage/cellcnt",  url_name='amfui/live_state_manage/cellcnt')
def get_cell_cnt(request):
    return Cell.objects.all().count()

@router.get("/live_state_manage_join",  url_name='amfui/live_state_manage/join/list')
def cur_date_data(request):

    cur_date = datetime.now().date()
    _start = cur_date - timedelta(days=0)
    _end = cur_date + timedelta(days=1)
    result = {}
    metrics = {'tot_online':  Sum('OnLine')}
    lsResults = list(LiveStateManage.objects.filter(Check1__gte=_start, Check1__lt=_end).values(
        'Cell_id', 'Cell__Name', 'Cell__CellID', 'Cell__Plant','Cell__Alarmi_id', 'Cell__Alarmi__AllarmString').annotate(**metrics))
    metrics = {
        'tot_adjustTM': Sum('PowerOnSec',filter=Q(Mode='调校模式')),
        'tot_poweron':  Sum('PowerOnSec'),
        'tot_workTM':   Sum('WorkingSec',filter=Q(Mode='普通模式')),
        'tot_idleTM':   Sum('IdleTMSec',filter=Q(Mode='普通模式')),
        'tot_parts':    Sum('FinishParts',filter=Q(Mode='普通模式'))}
    recResults = list(Record.objects.filter(StartTime__gte=_start, StartTime__lt=_end).values( 
        'Cell_id','Cell__Plant','Cell__Name','Cell__CellID',).annotate(
            **metrics))
    wsResults = list(Record.objects.filter(StartTime__gte=_start, StartTime__lt=_end, Status = '加工中').values( 
        'Cell_id','WorkSheet_id','WorkSheet__FinishParts','WorkSheet__Status', 'EstimatedSec','StartTime__date').annotate(
            TotReq = F('WorkSheet__AddReqParts')+F('WorkSheet__ReqParts')))
    for item in wsResults:
        if item['EstimatedSec'] is not None:
            item['EstimatedSec'] = sec2TmStr(item['EstimatedSec'])
    for item in recResults:
        for key in ['tot_poweron','tot_workTM','tot_idleTM','tot_adjustTM',]:
            if item[key] is not None:
                item[key] = sec2TmStr(item[key])
    for item in lsResults:
        if item['tot_online'] is not None:
            item['tot_online'] = sec2TmStr(item['tot_online'])

    for item in lsResults + recResults + wsResults:
        if str(item['Cell_id']) not in result:
            result[str(item['Cell_id'])] = copy.deepcopy(defule_CellDic)
            result[str(item['Cell_id'])].update(item)
        else:
            result[str(item['Cell_id'])].update(item)
    result = list(result.values())
    return result