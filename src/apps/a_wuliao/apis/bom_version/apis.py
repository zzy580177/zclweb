from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from django.db.models import Q, F, Value, CharField, Count
from django.db.models.functions import Concat

from apps.a_wuliao.models import *
from apps.a_wuliao.apis.bom_version.schemas import *

router = Router(tags=['bom_version'])


@router.post('/bom_version', url_name='a_wuliao/bom_version/create')
def create(request, payload: list[BomVersionIn]):
    success = []
    faileds = []
    errors = []
    existCnt = 0
    try:        
        existing_materials = {material.number: material for material in Material.objects.all()}
        new_versionsId = {}
        for v in BomVersion.objects.values('material').annotate(cnt=Count('version_id')):
            new_versionsId[v['material']] = f"BOM_M{v['material']}_{int(v['cnt']+1):05d}"
        existing_vers = {f"{v.material_id} {v.version}": v for v in BomVersion.objects.all()}
    except Exception as e:
        errors.append(f"批量查询失败: {str(e)} ")
        return {'success': False, 'data': {'faileds': [], 'success': [], 'Error': errors}}

    to_create = []
    for idx, item in enumerate(payload):
        try:
            item_dic = {}
            for key, value in item.dict().items():
                if 'material_' not in key:
                    item_dic[key] = dict(value) if hasattr(value, '__dict__') else value

            material_obj = existing_materials.get(item.material_number)
            if not material_obj:
                errors.append(f"{idx+1}: 未找到物料: {item.material_number} {item.material_model} {item.material_name} 请先添加后重试")
                faileds.append({'id': idx, 'status': False})
                continue

            existV_obj = existing_vers.get(f"{material_obj.material_id} {item.version}")
            if existV_obj is not None:
                existCnt += 1
                continue

            base_obj = None
            if item.base:
                base_obj = BomVersion.objects.filter(material=material_obj, version=item.base).first()
                if not base_obj:
                    errors.append(f"{idx+1}: 未找到{material_obj.material_id} {item.base}历史版本")
                    faileds.append({'id': idx, 'status': False})
                    continue

            item_dic['base'] = base_obj
            item_dic['material'] = material_obj
            item_dic['version_id'] = new_versionsId.get(material_obj.material_id, f"BOM_M{material_obj.material_id}_00001")

            to_create.append((idx, item_dic, item_dic['version_id']))

        except Exception as e:
            errors.append(f"{idx+1}: 批量查询失败: {str(e)} ")
            faileds.append({'id': idx, 'status': False})

    if to_create:
        try:
            bomVersions = [BomVersion(**item_dic) for idx, item_dic, versionId in to_create]
            created_objects = BomVersion.objects.bulk_create(bomVersions)
            for i, obj in enumerate(created_objects):
                idx, item_dic, version_id = to_create[i]
                success.append({'id': idx, 'created': True, 'version_id': obj.version_id})
        except Exception as e:
            for item in to_create:
                idx, item_dic, version_id = item
                errors.append(f"{idx+1}: 批量创建失败: {str(e)} ")
                faileds.append({'id': idx, 'status': False})

    data = {'faileds': faileds, 'success': success, 'Error': errors}
    data['message'] = f'{len(success)}条记录上传成功, {existCnt}条记录已存在, {len(faileds)}条记录上传失败'
    if errors:
        return {'success': False, 'data': data}
    return {'success': True, 'data': {'message': f'成功上传{len(success)}条记录, {existCnt}条记录已存在'}}

@router.get('/bom_version/{item_id}', response=BomVersionOut, url_name='a_wuliao/bom_version/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(BomVersion, id=item_id)
    return item

@router.get('/bom_version', response=List[BomVersionListOut], url_name='a_wuliao/bom_version/list')
@paginate
def list_items(request, material_model: str = None, material_number: str = None):
    filters = Q()    
    if material_model:
        filters &= Q(material__model=material_model)
    if material_number:
        filters &= Q(material__number=material_number)
    if filters:
        qs = BomVersion.objects.select_related('material').filter(filters)
        material_ids = set(qs.values_list('material_id', flat=True))
        all_versions = BomVersion.objects.filter(material_id__in=material_ids).values('material_id', 'version', 'version_id')

        material_history = {}
        for row in all_versions:
            mid = row['material_id']
            material_history.setdefault(mid, {'versions': [], 'version_ids': []})
            material_history[mid]['versions'].append(row['version'])
            material_history[mid]['version_ids'].append(row['version_id'])

        for obj in qs:
            mid = obj.material_id
            obj.history_versions = material_history.get(mid, {}).get('versions', [])
            obj.history_versionIds = material_history.get(mid, {}).get('version_ids', [])

    else:
        qs = BomVersion.objects.all()
    return qs

@router.put('/bom_version/{item_id}', response=BomVersionOut, url_name='a_wuliao/bom_version/update')
def update(request, item_id, payload: BomVersionIn):
    item = get_object_or_404(BomVersion, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/bom_version/{item_id}', response=BomVersionOut, url_name='a_wuliao/bom_version/partial_update')
def partial_update(request, item_id, payload: BomVersionIn):
    item = get_object_or_404(BomVersion, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/bom_version/{item_id}', url_name='a_wuliao/bom_version/destroy')
def destroy(request, item_id):
    item = get_object_or_404(BomVersion, id=item_id)
    item.delete()
    return responses.ok('已删除')
