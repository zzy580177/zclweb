from typing import List

from django.db.models import Exists
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses
from django_starter.lib.common import to_decimal, str_to_date

from apps.b_jihua.models import *
from apps.a_wuliao.models import Material
from apps.b_jihua.apis.order_parts.schemas import *
from apps.a_wuliao.models import BomVersion
from apps.d_paichan.models import *

router = Router(tags=['order_parts'])

@router.post('/order_parts',  url_name='b_jihua/order_parts/create')
def create(request, payload: List[OrderPartsIn]):
    success = []
    faileds = []
    errors = []
    if not payload and len(payload) == 0:
        return {'success': False, 'data': {'message': '没有提供任何数据'}}
    if payload[0].order_id is None or payload[0].order_id.strip() == '':
        return {'success': False, 'data': {'message': '订单编号不能为空'}}
    order_id = payload[0].order_id.strip()
    order_obj = get_object_or_404(Order, order_id=order_id)
    if not order_obj:
        return {'success': False, 'data': {'message': f'订单编号 {order_id} 不存在'}}
    try:
        target_material_numbers = {item.material_number for item in payload}          
        existing_parts = {part.material.number : part for part in OrderParts.objects.filter(order=order_obj)}
        existing_materials = {material.number : material for material in Material.objects.filter(number__in=target_material_numbers)}
        history_versions = {mat.number: list(BomVersion.objects.filter(material=mat).values_list('version', flat=True)) for mat in existing_materials.values()}
    except Exception as e:
        errors.append(f"批量查询失败: {str(e)} ")
    
    existCnt = 0
    to_create = []

    for idx, item in enumerate(payload):
        try:
            if item.material_number is None or item.material_number.strip() == '':
                continue
            if item.material_number in existing_parts:
                existCnt += 1
                continue
            material_obj = existing_materials.get(item.material_number) if existing_materials else None
            if not material_obj:
                errors.append(f"{idx+1}: 物料 {item.material_name} {item.material_number} 不存在 ")
                faileds.append({'id': idx, 'status': False, })
                continue
            if item.version not in history_versions.get(item.material_number, []):
                errors.append(f"{idx+1}: 物料 {item.material_name} {item.material_number} 不存在 Version:{item.version} ")
                faileds.append({'id': idx, 'status': False, })
                continue

            item_dic = {'material': material_obj, 'status': '新建', 'version': item.version, 
                        'deadline': str_to_date(item.deadline) if item.deadline else None,
                        'quantity': to_decimal(item.quantity), 'description': item.description, 'order': order_obj}

            to_create.append((idx, item_dic, item.order_id))
        except Exception as e:
            errors.append(f"{idx+1}: 批量查询失败: {str(e)} ")
            faileds.append({'id': idx, 'status': False, })
    if to_create:
        try:
            parts = []
            for idx, item_dic, _ in to_create:
                parts.append(OrderParts(**item_dic))
            OrderParts.objects.bulk_create(parts)
            for idx, item_dic, _ in to_create:
                success.append({'id': idx, 'status': True, })
        except Exception as e:
            errors.append(f"批量创建失败: {str(e)}")
            for idx, _, _, _ in to_create:
                faileds.append({'id': idx, 'status': False})
    
    data = {'faileds': faileds, 'success': success, 'Error': errors}
    data['message'] = f'{len(success)}条记录上传成功, {existCnt}条记录已存在, {len(faileds)}条记录上传失败'
    if(len(errors)>0):
        return {'success': False, 'data': data}
    return {'success': True, 'data': {'message': f'成功上传{len(success)}条记录, {existCnt}条记录已存在'}}



@router.get('/order_parts/{item_id}', response=OrderPartsOut, url_name='b_jihua/order_parts/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(OrderParts, order_id=item_id)
    return item


@router.get('/order_parts', response=List[OrderPartOut], url_name='b_jihua/order_parts/list')
@paginate
def list_items(request, order_id: str = None, material_id: str = None, material_number: str = None, status: str = None, material_model: str = None):
    # 修复：使用正确的Django查询语法过滤p_orderpart为None的记录（顶层部件）
    qs = OrderParts.objects.filter(p_orderpart__isnull=True)
    if order_id or material_id or material_number or status or material_model:
        if order_id:
            qs = qs.filter(order__order_id = order_id.strip())
        if material_id:
            qs = qs.filter(material_id = material_id.strip())
        if material_number:
            qs = qs.filter(material__number__icontains = material_number.strip())
        if status:
            qs = qs.filter(status__icontains = status.strip())
        if material_model:
            qs = qs.filter(material__model__icontains = material_model.strip())
        return qs
    return qs.order_by('material__model')

@router.put('/order_parts/{item_id}', response=OrderPartsOut, url_name='b_jihua/order_parts/update')
def update(request, item_id, payload: OrderPartsIn):
    try:
        item = get_object_or_404(OrderParts, id=item_id)
        updates = payload.dict(exclude_unset=True)
        for attr, value in updates.items():
            if value is None:
                continue

            if attr in ('delivery_day', 'deadline'):
                value = str_to_date(value)
            elif attr in ('quantity', 'defectives', 'deliveries', 'cost'):
                if (isinstance(value, str) and value.strip() == ''):
                    value = None
                else:
                    value = to_decimal(value)
            elif 'material' in attr:
                if attr == 'material':
                    material_obj = get_object_or_404(Material, number=value.split()[-1])
                elif attr == 'material_number':
                    material_obj = get_object_or_404(Material, number=value)
                elif attr == 'material_id':
                    material_obj = get_object_or_404(Material, material_id=value)
                else:
                    continue
                value = material_obj
                attr = 'material'
            elif 'order' in attr:
                order_obj = get_object_or_404(Order, order_id=value)
                value = order_obj
                attr = 'order'

            setattr(item, attr, value)
        item.save()
    except Exception as e:
        return {'success': False, 'data': {'message': f'更新失败: {str(e)}'}}
    return item

@router.patch('/order_parts/{item_id}', response=OrderPartsOut, url_name='b_jihua/order_parts/partial_update')
def partial_update(request, item_id, payload: OrderPartsIn):
    item = get_object_or_404(OrderParts, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/order_parts/{item_id}', url_name='b_jihua/order_parts/destroy')
def destroy(request, item_id):
    item = get_object_or_404(OrderParts, id=item_id)
    item.delete()
    return responses.ok('已删除')
