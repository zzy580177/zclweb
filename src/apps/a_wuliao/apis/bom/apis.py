from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate
from django.db.models import Q, F, Value, CharField, Count
from django_starter.http.response import responses
from django.db import transaction
from apps.a_wuliao.models import *
from apps.a_wuliao.apis.bom.schemas import *

router = Router(tags=['bom'])

@router.get('/get_material_vi_parents', response=List[SubBomOut], url_name='a_wuliao/bom/get_material_vi_parents')
def get_material_vi_parents(request, material_id: str, version: str):
    """获取指定物料版本的所有上级物料信息（直接上级和间接上级）"""
    try:
        p_material_obj = get_object_or_404(Material, material_id=material_id)
        if not p_material_obj:
            return []
        qs = Bom.objects.select_related('version', 'p_material').filter(
            p_material = p_material_obj,
            version__version = version)
    except Exception as e:
        return []
    return qs

@router.get('/get_materials', response=List[SubBomOut], url_name='a_wuliao/bom/get_materials')
def get_materials(request, material_id: str, version: str):
    try:
        p_material_obj = get_object_or_404(Material, material_id=material_id)
        if not p_material_obj:
            return []
        qs = Bom.objects.select_related('version', 'p_material').filter(
            Q(p_material=p_material_obj, version__version=version) | 
            Q(version__material=p_material_obj, version__version=version))
    except Exception as e:
        return []
    return qs

@router.post('/bom', response=dict, url_name='a_wuliao/bom/create')
def create(request, payload: List[BomIn]):
    """批量创建BOM记录"""
    success = []
    failed = [] 
    errors = []
    exist_count = 0  
    if not payload:
        return {'success': False, 'data': {'message': '请求数据为空'}}
    
    try:
        # 批量查询现有数据，优化性能
        existing_materials = {material.number: material for material in Material.objects.all()}
        existing_materials_pk = {str(material.pk): material for material in Material.objects.all()}
        existing_vers = {(bv.material_id, bv.version): bv for bv in BomVersion.objects.all()}        
        existing_bom = {(b.version_id, b.p_material.material_id if b.p_material else None): b for b in Bom.objects.all()}
        
    except Exception as e:
        errors.append(f"批量查询失败: {str(e)}")
        return {'success': False, 'data': {'failed': [], 'success': [], 'Error': errors}}

    to_create = []
    for idx, item in enumerate(payload):
        try:
            item_dic = {}
            for key, value in item.dict().items():
                if 'material' not in key:
                    item_dic[key] = dict(value) if hasattr(value, '__dict__') else value
            material_obj = existing_materials.get(item.material_number)
            if not material_obj:
                errors.append(f"{idx+1}: 未找到物料: {item.material_number} {item.material_model} {item.material_name} 请先添加后重试")
                failed.append({'id': idx, 'status': False})
                continue
            
            version_obj = existing_vers.get((material_obj.material_id, item.version))
            if not version_obj:
                errors.append(f"{idx+1}: 未找到物料版本: 物料编号 {item.material_number} 版本号 {item.version} 请先添加后重试")
                failed.append({'id': idx, 'status': False})
                continue
            
            # 处理上级物料
            p_material_obj = None
            p_material_raw = item.p_material
            if p_material_raw is not None and p_material_raw != "":
                p_raw_str = str(p_material_raw)
                if '.' in p_raw_str:
                    p_material_obj = existing_materials.get(p_raw_str)
                    if not p_material_obj:
                        errors.append(f"{idx+1}: 未找到上级物料编号:{p_raw_str} 请先添加后重试")
                        failed.append({'id': idx, 'status': False})
                        continue
                elif p_raw_str.isdigit():
                    p_material_obj = existing_materials_pk.get(p_raw_str)
                    if not p_material_obj:
                        errors.append(f"{idx+1}: 未找到上级物料ID:{p_raw_str} 请先添加后重试")
                        failed.append({'id': idx, 'status': False})
                        continue
                else:
                    errors.append(f"{idx+1}: 上级物料:{p_raw_str} 格式错误，请使用物料编号或ID")
                    failed.append({'id': idx, 'status': False})
                    continue
            
            existing_bom_obj = existing_bom.get((version_obj.pk, p_material_obj.material_id if p_material_obj else None))
            if existing_bom_obj is not None:
                exist_count += 1
                continue
            
            item_dic['version'] = version_obj
            item_dic['p_material'] = p_material_obj
            to_create.append((idx, item_dic, material_obj.material_id, str(item.version)))
        except Exception as e:
            errors.append(f"{idx+1}: 处理失败: {str(e)}")
            failed.append({'id': idx, 'status': False})
            continue

    if to_create:
        try:
            with transaction.atomic():
                boms = [Bom(**item_dic) for _, item_dic, _, _ in to_create]
                Bom.objects.bulk_create(boms)
            for idx, item_dic, _, _ in to_create:
                success.append({'id': idx, 'status': True})
        except Exception as e:
            errors.append(f"批量创建失败: {str(e)}")
            for idx, _, _, _ in to_create:
                failed.append({'id': idx, 'status': False})
    
    data = {'failed': failed, 'success': success, 'Error': errors}
    data['message'] = f'{len(success)}条记录上传成功, {exist_count}条记录已存在, {len(failed)}条记录上传失败'
    
    if errors:
        return {'success': False, 'data': data}
    return {'success': True, 'data': {'message': f'成功上传{len(success)}条记录, {exist_count}条记录已存在'}}

@router.get('/bom/{item_id}', response=BomOut, url_name='a_wuliao/bom/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(Bom, id=item_id)
    return item


@router.get('/bom', response=List[BomOut], url_name='a_wuliao/bom/list')
@paginate
def list_items(request):
    qs = Bom.objects.all()
    return qs

@router.put('/bom/{item_id}', response=BomOut, url_name='a_wuliao/bom/update')
def update(request, item_id, payload: BomIn):
    item = get_object_or_404(Bom, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/bom/{item_id}', response=BomOut, url_name='a_wuliao/bom/partial_update')
def partial_update(request, item_id, payload: BomIn):
    item = get_object_or_404(Bom, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/bom/{item_id}', url_name='a_wuliao/bom/destroy')
def destroy(request, item_id):
    item = get_object_or_404(Bom, id=item_id)
    item.delete()
    return responses.ok('已删除')
