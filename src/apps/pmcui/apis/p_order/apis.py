from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.pmcui.models import *
from apps.pmcui.apis.p_order.schemas import *

router = Router(tags=['p_order'])


@router.post('/p_order', response=POrderOut, url_name='pmcui/p_order/create')
def create(request, payload: POrderIn):
    item = POrder.objects.create(**payload.dict())
    return item


@router.get('/p_order/{item_id}', response=POrderOut, url_name='pmcui/p_order/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(POrder, id=item_id)
    return item


@router.get('/p_order', response=List[POrderOut], url_name='pmcui/p_order/list')
@paginate
def list_items(request):
    qs = POrder.objects.all()
    return qs


@router.put('/p_order/{item_id}', response=POrderOut, url_name='pmcui/p_order/update')
def update(request, item_id, payload: POrderIn):
    item = get_object_or_404(POrder, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/p_order/{item_id}', response=POrderOut, url_name='pmcui/p_order/partial_update')
def partial_update(request, item_id, payload: POrderIn):
    item = get_object_or_404(POrder, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/p_order/{item_id}', url_name='pmcui/p_order/destroy')
def destroy(request, item_id):
    item = get_object_or_404(POrder, id=item_id)
    item.delete()
    return responses.ok('已删除')