from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.amfui.models import *
from apps.amfui.apis.pezzi.schemas import *

router = Router(tags=['pezzi'])


@router.post('/pezzi', response=PezziOut, url_name='amfui/pezzi/create')
def create(request, payload: PezziIn):
    item = Pezzi.objects.create(**payload.dict())
    return item


@router.get('/pezzi/{item_id}', response=PezziOut, url_name='amfui/pezzi/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(Pezzi, id=item_id)
    return item


@router.get('/pezzi', response=List[PezziOut], url_name='amfui/pezzi/list')
@paginate
def list_items(request):
    qs = Pezzi.objects.all()
    return qs


@router.put('/pezzi/{item_id}', response=PezziOut, url_name='amfui/pezzi/update')
def update(request, item_id, payload: PezziIn):
    item = get_object_or_404(Pezzi, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/pezzi/{item_id}', response=PezziOut, url_name='amfui/pezzi/partial_update')
def partial_update(request, item_id, payload: PezziIn):
    item = get_object_or_404(Pezzi, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/pezzi/{item_id}', url_name='amfui/pezzi/destroy')
def destroy(request, item_id):
    item = get_object_or_404(Pezzi, id=item_id)
    item.delete()
    return responses.ok('已删除')