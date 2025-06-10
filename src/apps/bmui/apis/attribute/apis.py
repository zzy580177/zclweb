from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.bmui.models import *
from apps.bmui.apis.attribute.schemas import *

router = Router(tags=['attribute'])


@router.post('/attribute', response=AttributeOut, url_name='bmui/attribute/create')
def create(request, payload: AttributeIn):
    item = Attribute.objects.create(**payload.dict())
    return item


@router.get('/attribute/{item_id}', response=AttributeOut, url_name='bmui/attribute/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(Attribute, id=item_id)
    return item


@router.get('/attribute', response=List[AttributeOut], url_name='bmui/attribute/list')
@paginate
def list_items(request):
    qs = Attribute.objects.all()
    return qs


@router.put('/attribute/{item_id}', response=AttributeOut, url_name='bmui/attribute/update')
def update(request, item_id, payload: AttributeIn):
    item = get_object_or_404(Attribute, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/attribute/{item_id}', response=AttributeOut, url_name='bmui/attribute/partial_update')
def partial_update(request, item_id, payload: AttributeIn):
    item = get_object_or_404(Attribute, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/attribute/{item_id}', url_name='bmui/attribute/destroy')
def destroy(request, item_id):
    item = get_object_or_404(Attribute, id=item_id)
    item.delete()
    return responses.ok('已删除')