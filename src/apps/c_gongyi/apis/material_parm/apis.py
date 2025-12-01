from typing import List

from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses
from django_starter.lib.common import to_decimal

from apps.c_gongyi.models import *
from apps.a_wuliao.models import BomVersion
from apps.c_gongyi.apis.material_parm.schemas import *

router = Router(tags=['material_parm'])


@router.post('/material_parm', url_name='c_gongyi/material_parm/create')
def create(request, payload: List[MaterialParmIn]):
    success = []
    faileds = []
    errors = []
    # 限制查询到 payload 中涉及的物料/版本以减少全表扫描
    try:
        keys = {(item.material_number, item.version) for item in payload}
        numbers = {k for k, _ in keys}
        versions = {v for _, v in keys}
        existing_parm_qs = MaterialParm.objects.select_related('bom_ver__material').filter(
            bom_ver__material__number__in=numbers,
            bom_ver__version__in=versions,
        ) if keys else MaterialParm.objects.none()
        existing_parm = {(parm.bom_ver.material.number, parm.bom_ver.version): parm for parm in existing_parm_qs}

        existing_bomV_qs = BomVersion.objects.select_related('material').filter(
            material__number__in=numbers,
            version__in=versions,
        ) if keys else BomVersion.objects.none()
        existing_bomV = {(ver.material.number, ver.version): ver for ver in existing_bomV_qs}
    except Exception as e:
        errors.append(f"批量查询失败: {str(e)}")
        data = {'faileds': faileds, 'success': success, 'errors': errors}
        data['message'] = '批量查询失败，已终止操作'
        return {'success': False, 'data': data}
    existCnt = 0
    to_create = []

    for idx, item in enumerate(payload):
        try:
            if (item.material_number, item.version) in existing_parm:
                existCnt += 1
                continue
            if (item.material_number, item.version) not in existing_bomV:
                faileds.append({'id': idx, 'status': False, 'error': f"物料编号:{item.material_number},Version:{item.version} 不存在"})
                continue
            item_dic = {k: v for k, v in item.dict().items() if k not in ['material_number', 'version']}
            item_dic['bom_ver'] = existing_bomV.get((item.material_number, item.version))
            item_dic['cost'] = to_decimal(item.cost) if item.cost else None

            to_create.append((idx, item_dic, item.material_number))
        except Exception as e:
            errors.append(f"{idx+1}: 批量查询失败: {str(e)} ")
            faileds.append({'id': idx, 'status': False, })
    if to_create:
        try:
            parms = [MaterialParm(**item_dic) for _, item_dic, _ in to_create]
            with transaction.atomic():
                MaterialParm.objects.bulk_create(parms)
            for idx, _, _ in to_create:
                success.append({'id': idx, 'status': True})
        except IntegrityError as e:
            errors.append(f"批量创建失败(数据库完整性错误): {str(e)}")
            for idx, _, _ in to_create:
                faileds.append({'id': idx, 'status': False})
        except Exception as e:
            errors.append(f"批量创建失败: {str(e)}")
            for idx, _, _ in to_create:
                faileds.append({'id': idx, 'status': False})
    
    data = {'faileds': faileds, 'success': success, 'errors': errors}
    data['message'] = f'{len(success)}条记录上传成功, {existCnt}条记录已存在, {len(faileds)}条记录上传失败'
    if len(errors) > 0:
        return {'success': False, 'data': data}
    return {'success': True, 'data': {'message': f'成功上传{len(success)}条记录, {existCnt}条记录已存在'}}


@router.get('/material_parm/{item_id}', response=MaterialParmOut, url_name='c_gongyi/material_parm/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(MaterialParm, id=item_id)
    return item


@router.get('/material_parm', response=List[MaterialParmOut], url_name='c_gongyi/material_parm/list')
@paginate
def list_items(request, material_id: int = None,  version: str = None):
    qs = MaterialParm.objects.all()
    if material_id is not None:
        qs = qs.filter(bom_ver__material_id=material_id)
    if version is not None:
        qs = qs.filter(bom_ver__version=version)
    return qs


@router.put('/material_parm/{item_id}', response=MaterialParmOut, url_name='c_gongyi/material_parm/update')
def update(request, item_id, payload: MaterialParmIn):
    item = get_object_or_404(MaterialParm, id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/material_parm/{item_id}', response=MaterialParmOut, url_name='c_gongyi/material_parm/partial_update')
def partial_update(request, item_id, payload: MaterialParmIn):
    item = get_object_or_404(MaterialParm, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/material_parm/{item_id}', url_name='c_gongyi/material_parm/destroy')
def destroy(request, item_id):
    item = get_object_or_404(MaterialParm, id=item_id)
    item.delete()
    return responses.ok('已删除')