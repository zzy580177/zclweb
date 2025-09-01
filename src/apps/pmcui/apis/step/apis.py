from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.pmcui.models import *
from apps.pmcui.apis.step.schemas import *
from django.db.models import Q, F

router = Router(tags=['step'])


@router.post('/step', response=StepOut, url_name='pmcui/step/create')
def create(request, payload: StepIn):
    item = Step.objects.create(**payload.dict())
    return item


@router.get('/step/{item_id}', response=StepOut, url_name='pmcui/step/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(Step, id=item_id)
    return item


@router.get('/step', response=List[StepSampleOut], url_name='pmcui/step/list')
@paginate
def list_items(request, EqpType: int = None, EqpName: str = None):
    qs = Step.objects.select_related('EqpType')
    conditions = Q()
    if EqpName:
        conditions |= Q(EqpType__Name=EqpName)
    if EqpType:
        conditions |= Q(EqpType_id=EqpType)
    return qs.filter(conditions).annotate(EqpName=F('EqpType__Name'))


@router.put('/step/{item_id}', response=StepOut, url_name='pmcui/step/update')
def update(request, item_id, payload: StepIn):
    item = get_object_or_404(Step, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/step/{item_id}', response=StepOut, url_name='pmcui/step/partial_update')
def partial_update(request, item_id, payload: StepIn):
    item = get_object_or_404(Step, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/step/{item_id}', url_name='pmcui/step/destroy')
def destroy(request, item_id):
    item = get_object_or_404(Step, id=item_id)
    item.delete()
    return responses.ok('已删除')