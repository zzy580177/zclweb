from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses
from django.db.models import Q

from apps.pmcui.models import *
from apps.pmcui.apis.material_parm.schemas import *

router = Router(tags=['material_parm'])


@router.post('/material_parm', response=MaterialParmOut, url_name='pmcui/material_parm/create')
def create(request, payload: MaterialParmIn):
    item = MaterialParm.objects.create(**payload.dict())
    return item


@router.get('/material_parm/{item_id}', response=MaterialParmOut, url_name='pmcui/material_parm/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(MaterialParm, id=item_id)
    return item


@router.get('/material_parm', response=List[MaterialParmOut], url_name='pmcui/material_parm/list')
@paginate
def list_items(request, FName: str = None, FModel: str = None, FNumber: str = None):
    qs = MaterialParm.objects.select_related('Material')  # 关联 Material
    filters = Q()
    if FName:
        filters &= Q(Material__FName=FName)
    if FModel:
        filters &= Q(Material__FModel=FModel)
    if FNumber:
        filters &= Q(Material__FNumber=FNumber)
    if filters:
        qs = qs.filter(filters)
    return qs
    qs = qs.objects.all()
    return qs


@router.put('/material_parm/{item_id}', response=MaterialParmOut, url_name='pmcui/material_parm/update')
def update(request, item_id, payload: MaterialParmIn):
    item = get_object_or_404(MaterialParm, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/material_parm/{item_id}', response=MaterialParmOut, url_name='pmcui/material_parm/partial_update')
def partial_update(request, item_id, payload: MaterialParmIn):
    item = get_object_or_404(MaterialParm, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/material_parm/{item_id}', url_name='pmcui/material_parm/destroy')
def destroy(request, item_id):
    item = get_object_or_404(MaterialParm, id=item_id)
    item.delete()
    return responses.ok('已删除')