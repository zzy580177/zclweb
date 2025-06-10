from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate, PageNumberPagination

from django_starter.http.response import responses

from apps.pmcui.models import *
from apps.pmcui.apis.parts_order.schemas import *
from django.db.models import Q

router = Router(tags=['parts'])

class TenPerPagePagination(PageNumberPagination):
    page_size = 20

@router.post('/parts_order', response=PartsOrderOut, url_name='pmcui/parts_order/create')
def create(request, payload: PartsOrderIn):
    item = PartsOrder.objects.create(**payload.dict())
    return item


@router.get('/parts_order/{item_id}', response=PartsOrderOut, url_name='pmcui/parts_order/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(PartsOrder, id=item_id)
    return item


@router.get('/parts_order', response=List[PartsOrderOut], url_name='pmcui/parts_order/list')
@paginate
def list_items(request):
    qs = PartsOrder.objects.all()
    return qs

@router.get('/parts_list_by_order', response=List[PartsOrderOut], url_name='pmcui/parts_order/list_by_orderid')
@paginate(TenPerPagePagination)
def list_by_orderid(request, OrderId: str = None, FModel: str = None, FNumber: str = None):
    qs = PartsOrder.objects.select_related('Part')  # 关联 Material
    filters = Q()
    if OrderId:
        filters &= Q(POrder_id=OrderId)
    if FModel:
        filters &= Q(Part__FModel__icontains=FModel)
    if FNumber:
        filters &= Q(Part__FNumber__icontains=FNumber)
    if filters:
        qs = qs.filter(filters)
    return qs

@router.put('/parts_order/{item_id}', response=PartsOrderOut, url_name='pmcui/parts_order/update')
def update(request, item_id, payload: PartsOrderIn):
    item = get_object_or_404(PartsOrder, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/parts_order/{item_id}', response=PartsOrderOut, url_name='pmcui/parts_order/partial_update')
def partial_update(request, item_id, payload: PartsOrderIn):
    item = get_object_or_404(PartsOrder, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/parts_order/{item_id}', url_name='pmcui/parts_order/destroy')
def destroy(request, item_id):
    item = get_object_or_404(PartsOrder, id=item_id)
    item.delete()
    return responses.ok('已删除')