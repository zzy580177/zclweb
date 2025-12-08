from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router

from django_starter.http.response import responses

from apps.d_paichan.models import ProductionPlan
from apps.d_paichan.apis.production_plan.schemas import *

router = Router(tags=['production_plan'])

@router.post('/production_plan', response=ProductionPlanOut, url_name='d_paichan/production_plan/create')
def create(request, payload: ProductionPlanIn):
    item = ProductionPlan.objects.create(**payload.dict())
    return item

@router.get('/production_plan/{item_id}', response=ProductionPlanOut, url_name='d_paichan/production_plan/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(ProductionPlan, id=item_id)
    return item

@router.get('/production_plan', response=List[ProductionPlanOut], url_name='d_paichan/production_plan/list')
def list_items(request):
    qs = ProductionPlan.objects.all()
    return qs

@router.put('/production_plan/{item_id}', response=ProductionPlanOut, url_name='d_paichan/production_plan/update')
def update(request, item_id, payload: ProductionPlanIn):
    item = get_object_or_404(ProductionPlan, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item

@router.delete('/production_plan/{item_id}', url_name='d_paichan/production_plan/destroy')
def destroy(request, item_id):
    item = get_object_or_404(ProductionPlan, id=item_id)
    item.delete()
    return responses.ok('已删除')
