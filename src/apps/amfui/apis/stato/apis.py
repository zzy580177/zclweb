from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses
from django.db.models import Sum, Q, Count, CharField, F, Max
from apps.amfui.models import *
from apps.amfui.apis.stato.schemas import *

router = Router(tags=['stato'])


@router.post('/stato', response=StatoOut, url_name='amfui/stato/create')
def create(request, payload: StatoIn):
    item = Stato.objects.create(**payload.dict())
    return item


@router.get('/stato/{item_id}', response=StatoOut, url_name='amfui/stato/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(Stato, id=item_id)
    return item


@router.get('/stato', response=List[StatoOut], url_name='amfui/stato/list')
@paginate
def list_items(request):
    qs = Stato.objects.all()
    return qs


@router.put('/stato/{item_id}', response=StatoOut, url_name='amfui/stato/update')
def update(request, item_id, payload: StatoIn):
    item = get_object_or_404(Stato, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/stato/{item_id}', response=StatoOut, url_name='amfui/stato/partial_update')
def partial_update(request, item_id, payload: StatoIn):
    item = get_object_or_404(Stato, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/stato/{item_id}', url_name='amfui/stato/destroy')
def destroy(request, item_id):
    item = get_object_or_404(Stato, id=item_id)
    item.delete()
    return responses.ok('已删除')