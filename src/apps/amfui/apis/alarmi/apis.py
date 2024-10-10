from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.amfui.models import *
from apps.amfui.apis.alarmi.schemas import *

router = Router(tags=['alarmi'])


@router.post('/alarmi', response=AlarmiOut, url_name='amfui/alarmi/create')
def create(request, payload: AlarmiIn):
    item = Alarmi.objects.create(**payload.dict())
    return item


@router.get('/alarmi/{item_id}', response=AlarmiOut, url_name='amfui/alarmi/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(Alarmi, id=item_id)
    return item


@router.get('/alarmi', response=List[AlarmiOut], url_name='amfui/alarmi/list')
@paginate
def list_items(request):
    qs = Alarmi.objects.all()
    return qs


@router.put('/alarmi/{item_id}', response=AlarmiOut, url_name='amfui/alarmi/update')
def update(request, item_id, payload: AlarmiIn):
    item = get_object_or_404(Alarmi, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/alarmi/{item_id}', response=AlarmiOut, url_name='amfui/alarmi/partial_update')
def partial_update(request, item_id, payload: AlarmiIn):
    item = get_object_or_404(Alarmi, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/alarmi/{item_id}', url_name='amfui/alarmi/destroy')
def destroy(request, item_id):
    item = get_object_or_404(Alarmi, id=item_id)
    item.delete()
    return responses.ok('已删除')