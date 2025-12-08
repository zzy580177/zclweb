from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router

from django_starter.http.response import responses

from apps.d_paichan.models import ProductionOrder, ProductionPlan, WorkOrder
from apps.d_paichan.apis.production_order.schemas import *
from apps.c_gongyi.models import Process

router = Router(tags=['production_order'])

@router.post('/production_order', response=ProductionOrderOut, url_name='d_paichan/production_order/create')
def create(request, payload: ProductionOrderIn):
    item = ProductionOrder.objects.create(**payload.dict())
    return item

@router.post('/production_order/generate', url_name='d_paichan/production_order/generate')
def generate_from_plan(request, plan_id: int):
    plan = get_object_or_404(ProductionPlan, id=plan_id)
    # Generate order number, simple increment
    existing_orders = ProductionOrder.objects.filter(plan=plan).count()
    order_number = f"PO-{plan.id}-{existing_orders+1}"
    
    production_order = ProductionOrder.objects.create(
        plan=plan,
        order_number=order_number,
        quantity=plan.planned_quantity,
        status='generated'
    )
    return {'success': True, 'order': ProductionOrderOut.from_orm(production_order).dict()}

@router.get('/production_order/{item_id}', response=ProductionOrderOut, url_name='d_paichan/production_order/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(ProductionOrder, id=item_id)
    return item

@router.get('/production_order', response=List[ProductionOrderOut], url_name='d_paichan/production_order/list')
def list_items(request):
    qs = ProductionOrder.objects.all()
    return qs

@router.put('/production_order/{item_id}', response=ProductionOrderOut, url_name='d_paichan/production_order/update')
def update(request, item_id, payload: ProductionOrderIn):
    item = get_object_or_404(ProductionOrder, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item

@router.delete('/production_order/{item_id}', url_name='d_paichan/production_order/destroy')
def destroy(request, item_id):
    item = get_object_or_404(ProductionOrder, id=item_id)
    item.delete()
    return responses.ok('已删除')
