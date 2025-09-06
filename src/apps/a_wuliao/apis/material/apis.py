from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses
from django.db.models import Count, Q, F, Value, Max
from django.db.models.functions import Concat
from django.db.models.expressions import ExpressionWrapper
from django.db.models import IntegerField

from apps.a_wuliao.models import *
from apps.a_wuliao.apis.material.schemas import *

router = Router(tags=['material'])

@router.post('/material', url_name='a_wuliao/material/create')
def create(request, payload: list[MaterialIn]):
    success = []
    faileds = []
    errors = []
    existCnt = 0
    try:
        existing_vers = {v['material']: f"BOM_M{v['material']}_{int(v['cnt']+1):05d}" for v in 
            BomVersion.objects.values('material').annotate(cnt=Count('version_id'))}            
        existing_units = {unit.name: unit for unit in Attribute.objects.filter(description = '单位').all()}
        existing_groups = {group.number: group for group in MaterialGroup.objects.all()}
        existing_materials = {material.number: material for material in Material.objects.all()}
    except Exception as e:
        errors.append(f"批量查询失败: {str(e)} ")
    to_create = []
    bomVersions = []
    for idx, item in enumerate(payload):
        try:
            item_dic = item.dict()
            parent__number = '.'.join(item.number.split('.')[:-1])
            unit_obj = existing_units.get(item.unit)
            if not unit_obj:
                errors.append(f"{idx+1}: 未找到 属性单位: {item.unit} 请先添加后重试")
                faileds.append({'id': idx, 'status': False, })
                continue
            group_obj = existing_groups.get(parent__number)
            if not group_obj:
                errors.append(f"{idx+1}: 未找到{item.number}-{item.name}父节点")
                faileds.append({'id': idx, 'status': False, })
                continue
            item_dic['group'] = group_obj
            item_dic['unit'] = unit_obj
            if item.number in existing_materials:
                existCnt = existCnt + 1
            else:
                to_create.append((idx, item_dic, item.name))

        except Exception as e:
            errors.append(f"{idx+1}: 批量查询失败: {str(e)} ")
            faileds.append({'id': idx, 'status': False, })

    if to_create:
        try:
            materials = []
            bomVersions =[]
            for idx, item_dic, name in to_create:
                material = Material(**item_dic)
                materials.append(material)                 
            created_objects = Material.objects.bulk_create(materials)
            for i, obj in enumerate(created_objects):
                idx, _, name = to_create[i]
                success.append({'id': idx, 'created': True, 'name': obj.name})
                version_id = existing_vers.get(obj.material_id)  
                if not version_id:  
                     version_id = f'BOM_M{obj.material_id}_00001'
                bomVersions.append(BomVersion(version_id=version_id, material=obj,
                    version="V1.0", change_reason="初始版本创建", status="已发布", creator="管理员"))
            BomVersion.objects.bulk_create(bomVersions)
            
        except Exception as e:
            for idx, _, _ in to_create:
                errors.append(f"{idx+1}: 批量创建失败: {str(e)} ")
                faileds.append({'id': idx, 'status': False, })
    
    data = {'faileds': faileds, 'success': success, 'Error': errors}
    data['message'] = f'{len(success)}条记录上传成功, {existCnt}条记录已存在, {len(faileds)}条记录上传失败'
    if(len(errors)>0):
        return {'success': False, 'data': data}
    return {'success': True, 'data': {'message': f'成功上传{len(success)}条记录, {existCnt}条记录已存在'}}



@router.get('/material/{item_id}', response=MaterialOut, url_name='a_wuliao/material/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(Material, id=item_id)
    return item


@router.get('/material', response=List[MaterialSampleOut], url_name='a_wuliao/material/list')
@paginate
def list_items(request, material_model: str = None, material_number: str = None):

    filters = Q()    
    if material_model:
        filters &= Q(model=material_model)
    if material_number:
        filters &= Q(number=material_number)
    if filters:
        qs = Material.objects.filter(filters)
    else:
        qs = Material.objects.all()
    return qs.annotate(material_model=F('model'), 
                       material_number = F('number'), 
                       material_name = F('name'))


@router.put('/material/{item_id}', response=MaterialOut, url_name='a_wuliao/material/update')
def update(request, item_id, payload: MaterialIn):
    item = get_object_or_404(Material, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/material/{item_id}', response=MaterialOut, url_name='a_wuliao/material/partial_update')
def partial_update(request, item_id, payload: MaterialIn):
    item = get_object_or_404(Material, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/material/{item_id}', url_name='a_wuliao/material/destroy')
def destroy(request, item_id):
    item = get_object_or_404(Material, id=item_id)
    item.delete()
    return responses.ok('已删除')
