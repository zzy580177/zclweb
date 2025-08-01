from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.amfui.models import *
from apps.amfui.apis.cell.schemas import *

from django.db.models import Sum, F, Q, Value, IntegerField, Prefetch, Count
from django.db.models.functions import Coalesce, TruncDate, Concat

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

@router.get('/cncs',  url_name='amfui/cell/listcncs')
def list_cncs_items(request):
    rlist = {'cells':{},"msgs":{}}
    offlineCells = 0; idleCells = 0; jobCells = 0; abnormalCells = 0
    amfqs = Cell.objects.filter(Name='ZCL数采平台').prefetch_related(
        Prefetch('livestate_set', queryset=LiveState.objects.order_by('-Check1')[0:1], to_attr='latest_check1'))
    cellqs = Cell.objects.exclude(Name="ZCL数采平台").prefetch_related(
        Prefetch('livestate_set', queryset=LiveState.objects.order_by('-Check1')[0:1], to_attr='latest_check1'),
        Prefetch('stato_set', queryset=Stato.objects.order_by('-DataTime')[0:1], to_attr='latest_stato'))
    info = list(cellqs.filter(Q(Stato=3)).all())  
    for amf in amfqs:
        if amf.Name == 'ZCL数采平台':
            tm = amf.latest_check1[0].Check1
            isOffLine = (datetime.now() - tm) > timedelta(minutes=5) if amf.latest_check1 else False
            if isOffLine:
                offlineCells = offlineCells + cellqs.exclude(Name = 'ZCL数采平台').filter(Q(Plant=amf.Plant)).count()
                rlist["msgs"][tm.strftime('%m/%d %H:%M:%S ')] = tm.strftime('%m/%d %H:%M:%S ') + amf.Name +' '+ str(amf.CellID) + ' 已离线或故障中'
            else:
                idleCells = idleCells + cellqs.exclude(Name = 'ZCL数采平台').filter(Q(Plant=amf.Plant)& Q(Stato=0)).count()
                jobCells = jobCells + cellqs.exclude(Name = 'ZCL数采平台').filter(Q(Plant=amf.Plant)& Q(Stato=1)).count()
                abnormalCells = abnormalCells + cellqs.exclude(Name = 'ZCL数采平台').filter(Q(Plant=amf.Plant)& Q(Stato=2)).count()                
                offlineCells = offlineCells + cellqs.exclude(Name = 'ZCL数采平台').filter(Q(Plant=amf.Plant)& Q(Stato=3)).count()

    for cell in cellqs.filter(Q(Stato=2)).all():
        if cell.latest_stato:
            tm = cell.latest_stato[0].DataTime.strftime('%m/%d %H:%M:%S ')
            rlist["msgs"][tm] = tm + cell.Name +' '+ str(cell.CellID) + ' ' + cell.latest_stato[0].Alarmi.AlarmString
    for cell in cellqs.filter(Q(Stato=3)).all():
        if cell.latest_check1:
            tm = cell.latest_check1[0].Check1.strftime('%m/%d %H:%M:%S ')
            rlist["msgs"][tm] = tm + cell.Name +' '+ str(cell.CellID) + ' 已离线或故障中'
    rlist['cells']={'离线中':offlineCells, '待机中':idleCells,'作业中':jobCells, '故障中':abnormalCells};
    rlist['msgs'] = dict(sorted(rlist['msgs'].items(), key=lambda x: x[0], reverse=True))
 
    return rlist

