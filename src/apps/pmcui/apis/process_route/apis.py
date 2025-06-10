from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.pmcui.models import *
from apps.pmcui.apis.process_route.schemas import *

router = Router(tags=['process_route'])


@router.post('/process_route', response=ProcessRouteOut, url_name='pmcui/process_route/create')
def create(request, payload: ProcessRouteIn):
    item = ProcessRoute.objects.create(**payload.dict())
    return item


@router.get('/process_route/{item_id}', response=ProcessRouteOut, url_name='pmcui/process_route/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(ProcessRoute, id=item_id)
    return item


@router.get('/process_route', response=List[ProcessRouteOut], url_name='pmcui/process_route/list')
@paginate
def list_items(request):
    qs = ProcessRoute.objects.all()
    return qs


@router.put('/process_route/{item_id}', response=ProcessRouteOut, url_name='pmcui/process_route/update')
def update(request, item_id, payload: ProcessRouteIn):
    item = get_object_or_404(ProcessRoute, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/process_route/{item_id}', response=ProcessRouteOut, url_name='pmcui/process_route/partial_update')
def partial_update(request, item_id, payload: ProcessRouteIn):
    item = get_object_or_404(ProcessRoute, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/process_route/{item_id}', url_name='pmcui/process_route/destroy')
def destroy(request, item_id):
    item = get_object_or_404(ProcessRoute, id=item_id)
    item.delete()
    return responses.ok('已删除')