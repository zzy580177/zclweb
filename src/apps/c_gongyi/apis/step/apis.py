from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses
from django_starter.lib.common import to_decimal

from apps.c_gongyi.models import *
from apps.c_gongyi.apis.step.schemas import *

router = Router(tags=['step'])


@router.post('/step', url_name='c_gongyi/step/create')
def create(request, payload: list[StepIn]):
    success = []
    faileds = []
    errors = []
    try:          
        existing_step = {(step.name, step.type.name): step for step in Step.objects.all()}
        existing_types = {attr.name: attr for attr in Attribute.objects.filter(description='工序分类')}
    except Exception as e:
        errors.append(f"批量查询失败: {str(e)} ")
    existCnt = 0
    to_create = []

    for idx, item in enumerate(payload):
        try:
            if (item.name, item.type_name) in existing_step:
                existCnt += 1
                continue
            if item.type_name not in existing_types:
                faileds.append({'id': idx, 'status': False, 'error': f"工序分类[{item.type_name}]不存在"})
                continue
            item_dic = {k: v for k, v in item.dict().items() if k != 'type_name'}
            item_dic['type'] = existing_types[item.type_name]
            item_dic['ucost'] = to_decimal(item.ucost) if item.ucost else None
            item_dic['hcost'] = to_decimal(item.hcost) if item.hcost else None

            to_create.append((idx, item_dic, item.name))
        except Exception as e:
            errors.append(f"{idx+1}: 批量查询失败: {str(e)} ")
            faileds.append({'id': idx, 'status': False, })
    if to_create:
        try:
            steps = []
            for idx, item_dic, _ in to_create:
                steps.append(Step(**item_dic))
            Step.objects.bulk_create(steps)
            for idx, item_dic, _ in to_create:
                success.append({'id': idx, 'status': True, })
        except Exception as e:
            errors.append(f"批量创建失败: {str(e)}")
            for idx, _, _, in to_create:
                faileds.append({'id': idx, 'status': False})
    
    data = {'faileds': faileds, 'success': success, 'Error': errors}
    data['message'] = f'{len(success)}条记录上传成功, {existCnt}条记录已存在, {len(faileds)}条记录上传失败'
    if(len(errors)>0):
        return {'success': False, 'data': data}
    return {'success': True, 'data': {'message': f'成功上传{len(success)}条记录, {existCnt}条记录已存在'}}

@router.get('/step/{item_id}', response=StepOut, url_name='c_gongyi/step/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(Step, id=item_id)
    return item


@router.get('/step', response=List[StepOut], url_name='c_gongyi/step/list')
@paginate
def list_items(request, type_name: Optional[str] = None, name: Optional[str] = None):
    qs = Step.objects.all()
    if type_name:
        qs = qs.filter(type__name=type_name)
    if name:
        qs = qs.filter(name__icontains=name)
    return qs


@router.put('/step/{item_id}', response=StepOut, url_name='c_gongyi/step/update')
def update(request, item_id, payload: StepIn):
    item = get_object_or_404(Step, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/step/{item_id}', response=StepOut, url_name='c_gongyi/step/partial_update')
def partial_update(request, item_id, payload: StepIn):
    item = get_object_or_404(Step, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/step/{item_id}', url_name='c_gongyi/step/destroy')
def destroy(request, item_id):
    item = get_object_or_404(Step, id=item_id)
    item.delete()
    return responses.ok('已删除')