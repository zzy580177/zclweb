from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.pmcui.models import *
from apps.pmcui.apis.virtual_process_route.schemas import *

router = Router(tags=['virtual_process_route'])


@router.post('/virtual_process_route', response=VirtualProcessRouteOut, url_name='pmcui/virtual_process_route/create')
def create(request, payload: VirtualProcessRouteIn):
    item = VirtualProcessRoute.objects.create(**payload.dict())
    return item


@router.get('/virtual_process_route/{item_id}', response=VirtualProcessRouteOut, url_name='pmcui/virtual_process_route/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(VirtualProcessRoute, id=item_id)
    return item


@router.get('/virtual_process_route', response=List[VirtualProcessRouteOut], url_name='pmcui/virtual_process_route/list')
@paginate
def list_items(request):
    qs = VirtualProcessRoute.objects.all()
    return qs


@router.put('/virtual_process_route/{item_id}', response=VirtualProcessRouteOut, url_name='pmcui/virtual_process_route/update')
def update(request, item_id, payload: VirtualProcessRouteIn):
    item = get_object_or_404(VirtualProcessRoute, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/virtual_process_route/{item_id}', response=VirtualProcessRouteOut, url_name='pmcui/virtual_process_route/partial_update')
def partial_update(request, item_id, payload: VirtualProcessRouteIn):
    item = get_object_or_404(VirtualProcessRoute, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/virtual_process_route/{item_id}', url_name='pmcui/virtual_process_route/destroy')
def destroy(request, item_id):
    item = get_object_or_404(VirtualProcessRoute, id=item_id)
    item.delete()
    return responses.ok('已删除')