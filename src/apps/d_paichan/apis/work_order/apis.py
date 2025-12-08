from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router

from django_starter.http.response import responses

from apps.d_paichan.models import WorkOrder, ProductionOrder
from apps.d_paichan.apis.work_order.schemas import *
from apps.c_gongyi.models import Process, Craft

router = Router(tags=['work_order'])

@router.post('/work_order', response=WorkOrderOut, url_name='d_paichan/work_order/create')
def create(request, payload: WorkOrderIn):
    item = WorkOrder.objects.create(**payload.dict())
    return item

@router.post('/work_order/generate', url_name='d_paichan/work_order/generate')
def generate_from_production_order(request, production_order_id: int):
    production_order = get_object_or_404(ProductionOrder, id=production_order_id)
    plan = production_order.plan
    route = plan.route
    
    # Get steps from route
    processes = Process.objects.filter(route=route).order_by('seqnum')
    
    work_orders = []
    seq = 1
    for process in processes:
        for craft in Craft.objects.filter(process=process):
            work_order = WorkOrder.objects.create(
                production_order=production_order,
                step=craft.step,
                sequence=seq,
                quantity=production_order.quantity,
                status='pending'
            )
            work_orders.append(WorkOrderOut.from_orm(work_order).dict())
            seq += 1
    
    return {'success': True, 'work_orders': work_orders}

@router.get('/work_order/{item_id}', response=WorkOrderOut, url_name='d_paichan/work_order/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(WorkOrder, id=item_id)
    return item

@router.get('/work_order', response=List[WorkOrderOut], url_name='d_paichan/work_order/list')
def list_items(request):
    qs = WorkOrder.objects.all()
    return qs

@router.put('/work_order/{item_id}', response=WorkOrderOut, url_name='d_paichan/work_order/update')
def update(request, item_id, payload: WorkOrderIn):
    item = get_object_or_404(WorkOrder, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item

@router.delete('/work_order/{item_id}', url_name='d_paichan/work_order/destroy')
def destroy(request, item_id):
    item = get_object_or_404(WorkOrder, id=item_id)
    item.delete()
    return responses.ok('已删除')
