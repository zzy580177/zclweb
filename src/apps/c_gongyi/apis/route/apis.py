from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.c_gongyi.models import *
from apps.c_gongyi.apis.route.schemas import *

router = Router(tags=['route'])


@router.post('/route', response=RouteOut, url_name='c_gongyi/route/create')
def create(request, payload: RouteIn):
    item = Route.objects.create(**payload.dict())
    return item


@router.get('/route/{item_id}', response=RouteOut, url_name='c_gongyi/route/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(Route, id=item_id)
    return item

@router.get('/material/{item_id}', response=List[RouteOut], url_name='c_gongyi/route/material_route')
def get_route_by_material(request, item_id):
    item = Route.objects.filter(bom_ver__material_id=item_id).order_by('-route_ver')
    return item

@router.get('/route', response=List[RouteOut], url_name='c_gongyi/route/list')
@paginate
def list_items(request):
    qs = Route.objects.all()
    return qs


@router.put('/route/{item_id}', response=RouteOut, url_name='c_gongyi/route/update')
def update(request, item_id, payload: RouteIn):
    item = get_object_or_404(Route, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/route/{item_id}', response=RouteOut, url_name='c_gongyi/route/partial_update')
def partial_update(request, item_id, payload: RouteIn):
    item = get_object_or_404(Route, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/route/{item_id}', url_name='c_gongyi/route/destroy')
def destroy(request, item_id):
    item = get_object_or_404(Route, id=item_id)
    item.delete()
    return responses.ok('已删除')
