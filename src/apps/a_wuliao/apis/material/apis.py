from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses
from django.db.models import Count, Q, F, Value, Max
from django.db.models.functions import Concat
from django.db.models.expressions import ExpressionWrapper
from django.db.models import IntegerField
from django.db import transaction

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
        existing_units = {unit.name: unit for unit in Attribute.objects.filter(description = '单位').all()}
        existing_groups = {group.number: group for group in MaterialGroup.objects.all()}
        existing_materials = {material.number: material for material in Material.objects.all()}
        existing_materials_pk = {material.pk: material for material in Material.objects.all()}
    except Exception as e:
        errors.append(f"批量查询失败: {str(e)} ")

    to_create = []
    p_material_map = {}    # 存放 material_number -> resolved 父物料对象（Model 或 None）
    seen_numbers = set()   # 防止 payload 内重复创建同一编号

    for idx, item in enumerate(payload):
        try:
            item_dic = {}
            p_material_raw = item.p_material
            item_dic = {k: v for k, v in item.dict().items() if k != 'p_material'}

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

            p_material_obj = None
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
            item_dic['group'] = group_obj
            item_dic['unit'] = unit_obj
            if item.number in existing_materials or item.number in seen_numbers:
                existCnt += 1
                continue
            seen_numbers.add(item.number)
            to_create.append((idx, item_dic, item.name, p_material_obj))
            p_material_map[item.number] = p_material_obj
        except Exception as e:
            errors.append(f"{idx+1}: 批量查询失败: {str(e)} ")
            faileds.append({'id': idx, 'status': False, })

    if to_create:
        try:
            with transaction.atomic():
                materials = []
                for idx, item_dic, name, _ in to_create:
                    materials.append(Material(**item_dic))
                created_objects = Material.objects.bulk_create(materials)

                bomVersions = []
                boms = []
                for i, obj in enumerate(created_objects):
                    bomVersions.append(BomVersion(material=obj,
                        version="V1.0", change_reason="初始版本创建", status="已发布", creator="管理员"))
                createdBomV_objects = BomVersion.objects.bulk_create(bomVersions)
                material_ids = [obj.pk for obj in created_objects]
                saved_bv_map = {(bv.material_id, bv.version): bv for bv in 
                    BomVersion.objects.filter(material_id__in=material_ids, version="V1.0")}

                for i, obj in enumerate(created_objects):
                    idx, _, name, p_mat_obj = to_create[i]
                    success.append({'id': idx, 'created': True, 'name': obj.name})
                    bv = saved_bv_map.get((obj.pk,"V1.0")) or (createdBomV_objects[i] if i < len(createdBomV_objects) else None)
                    if bv is None or getattr(bv, 'pk', None) is None:
                        raise RuntimeError(f"无法获取已保存的 BomVersion 主键 (material={obj.pk})")
                    boms.append(Bom(version=bv, p_material=p_mat_obj))
                Bom.objects.bulk_create(boms)
            
        except Exception as e:
            errors.append(f"批量创建失败: {str(e)}")
            for idx, _, _, _ in to_create:
                faileds.append({'id': idx, 'status': False})
    
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
        if attr != 'p_material':
            setattr(item, attr, value)
    item.save()
    return item


@router.patch('/material/{item_id}', response=MaterialOut, url_name='a_wuliao/material/partial_update')
def partial_update(request, item_id, payload: MaterialIn):
    item = get_object_or_404(Material, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        if attr != 'p_material':
            setattr(item, attr, value)
    item.save()
    return item


@router.delete('/material/{item_id}', url_name='a_wuliao/material/destroy')
def destroy(request, item_id):
    item = get_object_or_404(Material, id=item_id)
    item.delete()
    return responses.ok('已删除')
