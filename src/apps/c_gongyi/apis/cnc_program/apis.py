from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.c_gongyi.models import *
from apps.c_gongyi.apis.cnc_program.schemas import *

router = Router(tags=['cnc_program'])


@router.post('/cnc_program', response=CNCProgramOut, url_name='c_gongyi/cnc_program/create')
def create(request, payload: CNCProgramIn):
    item = CNCProgram.objects.create(**payload.dict())
    return item


@router.get('/cnc_program/{item_id}', response=CNCProgramOut, url_name='c_gongyi/cnc_program/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(CNCProgram, id=item_id)
    return item


@router.get('/cnc_program', response=List[CNCProgramOut], url_name='c_gongyi/cnc_program/list')
@paginate
def list_items(request):
    qs = CNCProgram.objects.all()
    return qs


@router.put('/cnc_program/{item_id}', response=CNCProgramOut, url_name='c_gongyi/cnc_program/update')
def update(request, item_id, payload: CNCProgramIn):
    item = get_object_or_404(CNCProgram, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/cnc_program/{item_id}', response=CNCProgramOut, url_name='c_gongyi/cnc_program/partial_update')
def partial_update(request, item_id, payload: CNCProgramIn):
    item = get_object_or_404(CNCProgram, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/cnc_program/{item_id}', url_name='c_gongyi/cnc_program/destroy')
def destroy(request, item_id):
    item = get_object_or_404(CNCProgram, id=item_id)
    item.delete()
    return responses.ok('已删除')