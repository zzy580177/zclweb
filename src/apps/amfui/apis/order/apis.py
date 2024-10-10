from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.amfui.models import *
from apps.amfui.apis.order.schemas import *

router = Router(tags=['order'])


@router.post('/order', response=OrderOut, url_name='amfui/order/create')
def create(request, payload: OrderIn):
    item = Order.objects.create(**payload.dict())
    return item


@router.get('/order/{item_id}', response=OrderOut, url_name='amfui/order/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(Order, id=item_id)
    return item


@router.get('/order', response=List[OrderOut], url_name='amfui/order/list')
@paginate
def list_items(request):
    qs = Order.objects.all()
    return qs


@router.put('/order/{item_id}', response=OrderOut, url_name='amfui/order/update')
def update(request, item_id, payload: OrderIn):
    item = get_object_or_404(Order, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/order/{item_id}', response=OrderOut, url_name='amfui/order/partial_update')
def partial_update(request, item_id, payload: OrderIn):
    item = get_object_or_404(Order, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/order/{item_id}', url_name='amfui/order/destroy')
def destroy(request, item_id):
    item = get_object_or_404(Order, id=item_id)
    item.delete()
    return responses.ok('已删除')