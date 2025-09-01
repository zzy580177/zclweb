from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.pmcui.models import *
from apps.pmcui.apis.process_route.schemas import *

from django.db.models import Q, F

router = Router(tags=['process_route'])


@router.post('/process_route', response=ProcessRouteOut, url_name='pmcui/process_route/create')
def create(request, payload: ProcessRouteIn):
    item = ProcessRoute.objects.create(**payload.dict())
    return item


@router.get('/process_route/{item_id}', response=ProcessRouteOut, url_name='pmcui/process_route/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(ProcessRoute, Id=item_id)
    return item

@router.get('/process_route', response=List[ProcessRouteOut], url_name='pmcui/process_route/list')
@paginate
def list_items(request, Frelate = False, material_id: int = None, FNumber: str = None):
    qs = ProcessRoute.objects.all()
    if material_id:
        qs = qs.filter(Material_id=material_id)
    if FNumber:
        qs = qs.filter(Material__FNumber=FNumber)
    return qs

from django.db.models import Prefetch
from apps.pmcui.models import ProcessStep

from apps.pmcui.apis.process_step.schemas import ProcessStepOut

@router.get('/process_route_steps/{item_id}', response=ProcessRouteOut, url_name='pmcui/process_route/retrieve_steps')
def retrieve_steps(request, item_id):
    item = get_object_or_404(ProcessRoute, Id=item_id)
    return item

@router.get('/process_route_steps', response=List[ProcessRouteOut], url_name='pmcui/process_route/list_step')
def list_step_items(request, FId: int = None):
    qs = ProcessRoute.objects.filter(Material_id=FId).select_related('Material').all()
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

@router.get('/fullsteps/{item_id}', response=SampleProcessRouteOut, url_name='pmcui/process_route/fullsteps')
def fullsteps(request, item_id):
    qs = ProcessRoute.objects.filter(Id=item_id).prefetch_related(
            Prefetch('main_steps', queryset=ProcessStep.objects.prefetch_related('Steps')),
            'Material')   
    return qs.first()