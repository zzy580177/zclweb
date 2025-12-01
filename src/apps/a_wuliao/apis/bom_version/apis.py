from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from django.db.models import Q, F, Value, CharField, Count
from django.db.models.functions import Concat
from django.db import transaction, IntegrityError, connection
import re

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
        taret_material_numbers = {item.material_number for item in payload} 
        existing_materials = {material.number: material for material in Material.objects.all()}
        existing_materials_pk = {material.pk: material for material in Material.objects.all()}
        existing_vers = {f"{bv.material_id} {bv.version}": bv for bv in BomVersion.objects.all()}
    except Exception as e:
        errors.append(f"批量查询失败: {str(e)} ")
        return {'success': False, 'data': {'faileds': [], 'success': [], 'Error': errors}}

    to_create = []
    p_material_map ={}
    for idx, item in enumerate(payload):
        try:
            item_dic = {}
            for key, value in item.dict().items():
                if 'material' not in key:
                    item_dic[key] = dict(value) if hasattr(value, '__dict__') else value

            material_obj = existing_materials.get(item.material_number)
            if not material_obj:
                errors.append(f"{idx+1}: 未找到物料: {item.material_number} {item.material_model} {item.material_name} 请先添加后重试")
                faileds.append({'id': idx, 'status': False})
                continue
            p_material_obj = None
            p_material_raw = item.p_material
            if p_material_raw is not None and p_material_raw != "":
                p_raw_str = str(p_material_raw)
                if '.' in p_raw_str:
                    p_material_obj = existing_materials.get(p_raw_str)
                    if not p_material_obj:
                        errors.append(f"{idx+1}: 未找到上级物料编号:{p_raw_str} 请先添加后重试")
                        faileds.append({'id': idx, 'status': False})
                        continue
                elif p_raw_str.isdigit():
                    p_material_obj = existing_materials_pk.get(p_raw_str)
                    if not p_material_obj:
                        errors.append(f"{idx+1}: 未找到上级物料ID:{p_raw_str} 请先添加后重试")
                        faileds.append({'id': idx, 'status': False})
                        continue
                else:
                    errors.append(f"{idx+1}: 上级物料:{p_raw_str} 格式错误，请使用物料编号或ID")
                    faileds.append({'id': idx, 'status': False})
                    continue
            existV_obj = existing_vers.get(f"{material_obj.material_id} {item.version}")
            if existV_obj is not None:
                existCnt += 1
                continue

            base_obj = None
            if item.base:
                base_obj = existing_vers.get(f"{material_obj.material_id} {item.base}")
                if not base_obj:
                    errors.append(f"{idx+1}: 未找到{material_obj.material_id} {item.base}历史版本")
                    faileds.append({'id': idx, 'status': False})
                    continue

            item_dic['base'] = base_obj
            item_dic['material'] = material_obj
            to_create.append((idx, item_dic, material_obj.material_id, str(item.version)))
            p_material_map[material_obj.pk] = p_material_obj
        except Exception as e:
            errors.append(f"{idx+1}: 批量查询失败: {str(e)} ")
            faileds.append({'id': idx, 'status': False})

    if to_create:
        try:
            with transaction.atomic():
                bomVersions = [BomVersion(**item_dic) for idx, item_dic, _, _ in to_create]
                created_objects = BomVersion.objects.bulk_create(bomVersions)

                material_ids = [mid for _, _, mid, _ in to_create]
                versions = [ver for _, _, _, ver in to_create]
                saved_qs = BomVersion.objects.filter(material_id__in=material_ids, version__in=versions)
                saved_map = {(bv.material_id, str(bv.version)): bv for bv in saved_qs}

                boms_to_create = []
                for j, (idx, _, mid, ver) in enumerate(to_create, start=1):
                    bv = saved_map.get((mid, ver))
                    if bv is None or getattr(bv, 'pk', None) is None:
                        errors.append(f"{idx+1}: 创建失败，无法确认保存的 BomVersion (material={mid}, version={ver})")
                        faileds.append({'id': idx, 'status': False})
                        continue
                    boms_to_create.append(Bom(version=bv, p_material=p_material_map.get(mid)))

                if boms_to_create:
                    Bom.objects.bulk_create(boms_to_create)

                for i, (idx, _, mid, ver) in enumerate(to_create):
                    bv_obj = saved_map.get((mid, ver))
                    if bv_obj and getattr(bv_obj, 'pk', None):
                        success.append({'id': idx, 'created': True, 'version': bv_obj.version, 'material_id': bv_obj.material_id})

        except IntegrityError as e:
            errors.append(f"批量创建失败: 唯一性约束冲突或并发插入: {str(e)}")
            for idx, _, _, _ in to_create:
                faileds.append({'id': idx, 'status': False})
        except Exception as e:
            errors.append(f"批量创建失败: {str(e)}")
            for idx, _, _, _ in to_create:
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
    else:
        qs = BomVersion.objects.all()
    return qs

@router.put('/bom_version/{item_id}', response=BomVersionOut, url_name='a_wuliao/bom_version/update')
def update(request, item_id, payload: BomVersionIn):
    item = get_object_or_404(BomVersion, id=item_id)
    for attr, value in payload.dict().items():
        if attr != 'p_material':
            setattr(item, attr, value)
    item.save()
    return item


@router.patch('/bom_version/{item_id}', response=BomVersionOut, url_name='a_wuliao/bom_version/partial_update')
def partial_update(request, item_id, payload: BomVersionIn):
    item = get_object_or_404(BomVersion, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        if attr != 'p_material':
            setattr(item, attr, value)
    item.save()
    return item


@router.delete('/bom_version/{item_id}', url_name='a_wuliao/bom_version/destroy')
def destroy(request, item_id):
    item = get_object_or_404(BomVersion, id=item_id)
    item.delete()
    return responses.ok('已删除')
