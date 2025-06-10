from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.jihuaManagerUI.models import *
from apps.jihuaManagerUI.apis.out_bound_manag.schemas import *

router = Router(tags=['out_bound_manag'])


@router.post('/out_bound_manag', response=OutBoundManagOut, url_name='jihuaManagerUI/out_bound_manag/create')
def create(request, payload: OutBoundManagIn):
    item = OutBoundManag.objects.create(**payload.dict())
    return item


@router.get('/out_bound_manag/{item_id}', response=OutBoundManagOut, url_name='jihuaManagerUI/out_bound_manag/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(OutBoundManag, id=item_id)
    return item


@router.get('/out_bound_manag', response=List[OutBoundManagOut], url_name='jihuaManagerUI/out_bound_manag/list')
@paginate
def list_items(request):
    qs = OutBoundManag.objects.all()
    return qs


@router.put('/out_bound_manag/{item_id}', response=OutBoundManagOut, url_name='jihuaManagerUI/out_bound_manag/update')
def update(request, item_id, payload: OutBoundManagIn):
    item = get_object_or_404(OutBoundManag, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/out_bound_manag/{item_id}', response=OutBoundManagOut, url_name='jihuaManagerUI/out_bound_manag/partial_update')
def partial_update(request, item_id, payload: OutBoundManagIn):
    item = get_object_or_404(OutBoundManag, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/out_bound_manag/{item_id}', url_name='jihuaManagerUI/out_bound_manag/destroy')
def destroy(request, item_id):
    item = get_object_or_404(OutBoundManag, id=item_id)
    item.delete()
    return responses.ok('已删除')