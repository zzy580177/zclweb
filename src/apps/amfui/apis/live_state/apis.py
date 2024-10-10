from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.amfui.models import *
from apps.amfui.apis.live_state.schemas import *

router = Router(tags=['live_state'])


@router.post('/live_state', response=LiveStateOut, url_name='amfui/live_state/create')
def create(request, payload: LiveStateIn):
    item = LiveState.objects.create(**payload.dict())
    return item


@router.get('/live_state/{item_id}', response=LiveStateOut, url_name='amfui/live_state/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(LiveState, id=item_id)
    return item


@router.get('/live_state', response=List[LiveStateOut], url_name='amfui/live_state/list')
@paginate
def list_items(request):
    qs = LiveState.objects.all()
    return qs


@router.put('/live_state/{item_id}', response=LiveStateOut, url_name='amfui/live_state/update')
def update(request, item_id, payload: LiveStateIn):
    item = get_object_or_404(LiveState, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/live_state/{item_id}', response=LiveStateOut, url_name='amfui/live_state/partial_update')
def partial_update(request, item_id, payload: LiveStateIn):
    item = get_object_or_404(LiveState, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/live_state/{item_id}', url_name='amfui/live_state/destroy')
def destroy(request, item_id):
    item = get_object_or_404(LiveState, id=item_id)
    item.delete()
    return responses.ok('已删除')