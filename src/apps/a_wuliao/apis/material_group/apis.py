from typing import List
from django.db import transaction
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate
from django.core.cache import cache

from django_starter.http.response import responses

from apps.a_wuliao.models import *
from apps.a_wuliao.apis.material_group.schemas import *

router = Router(tags=['material_group'])


@router.post('/material_group', url_name='a_wuliao/material_group/create')
@transaction.atomic
def create(request, payload: list[MaterialGroupIn]):
    success = []
    faileds = []
    errors = []
    existCnt = 0

    existing_groups = {group.number: group for group in MaterialGroup.objects.all()}
    to_create = []
    
    for idx, item in enumerate(payload):
        try:
            item_dic = item.dict()
            item_dic['level'] = item.number.count('.')
            number_sl = item.number.split('.')
            
            if(item_dic['level'] > 0):
                item_dic['group'] = number_sl[0]
                parent__number = item_dic['group']
            if(item_dic['level'] >1):
                item_dic['sub_group'] = '.'.join(number_sl[0:2]) 
                parent__number = item_dic['sub_group']
            if(item_dic['level'] >2):
                item_dic['min_group'] = '.'.join(number_sl[0:3])
                parent__number = item_dic['min_group']
            if(item_dic['level'] >3):
                parent__number = '.'.join(number_sl[0:4])
            
            if item_dic['level'] > 0:
                obj = existing_groups.get(parent__number)
                if not obj:
                    errors.append(f"{idx+1}: 未找到{item.number}-{item.name}父节点")
                    faileds.append({'id': idx, 'status': False, })
                    continue
                item_dic['parent'] = obj
            else:
                item_dic['parent'] = None

            if item.number in existing_groups:
                existCnt = existCnt + 1
                #success.append({'id': idx, 'created': False, 'name': existing_obj.name, 'message': '记录已存在'})
            else:
                to_create.append((idx, item_dic, item.name))
            
        except Exception as e:
            errors.append(f"{idx+1}: 批量查询失败: {str(e)} ")
            faileds.append({'id': idx, 'status': False, })


    if to_create:
        try:
            material_groups = []
            for idx, item_dic, name in to_create:
                #item_dic.pop('group_id', None)
                material_group = MaterialGroup(**item_dic)
                material_groups.append(material_group)
            
            created_objects = MaterialGroup.objects.bulk_create(material_groups)

            for i, obj in enumerate(created_objects):
                idx, _, name = to_create[i]
                existing_groups[obj.number] = obj
                success.append({'id': idx, 'created': True, 'name': obj.name})
                
        except Exception as e:
            for idx, _, _ in to_create:
                errors.append(f"{idx+1}: 批量创建失败: {str(e)} ")
                faileds.append({'id': idx, 'status': False, })
    
    data = {'faileds': faileds, 'success': success, 'Error': errors}
    data['message'] = f'{len(success)}条记录上传成功, {existCnt}条记录已存在, {len(faileds)}条记录上传失败'
    if(len(errors)>0):
        return {'success': False, 'data': data}
    return {'success': True, 'data': {'message': f'成功上传{len(success)}条记录, {existCnt}条记录已存在'}}

@router.get('/material_group/{item_id}', response=MaterialGroupOut, url_name='a_wuliao/material_group/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(MaterialGroup, id=item_id)
    return item


@router.get('/material_group', response=List[MaterialGroupOut], url_name='a_wuliao/material_group/list')
@paginate
def list_items(request):
    qs = MaterialGroup.objects.all()
    return qs


@router.put('/material_group/{item_id}', response=MaterialGroupOut, url_name='a_wuliao/material_group/update')
def update(request, item_id, payload: MaterialGroupIn):
    item = get_object_or_404(MaterialGroup, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/material_group/{item_id}', response=MaterialGroupOut, url_name='a_wuliao/material_group/partial_update')
def partial_update(request, item_id, payload: MaterialGroupIn):
    item = get_object_or_404(MaterialGroup, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/material_group/{item_id}', url_name='a_wuliao/material_group/destroy')
def destroy(request, item_id):
    item = get_object_or_404(MaterialGroup, id=item_id)
    item.delete()
    return responses.ok('已删除')
