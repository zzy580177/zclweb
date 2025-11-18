from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses
from django_starter.lib.common import to_decimal

from apps.b_jihua.models import *
from apps.a_wuliao.models import Material
from apps.b_jihua.apis.order_parts.schemas import *

router = Router(tags=['order_parts'])
from datetime import datetime
day_format = "%Y-%m-%d"
day_format_s = "%Y%m%d"

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
        existing_parts = {part.material.number : part for part in OrderParts.objects.filter(order=order_obj)}
        existing_materials = {material.number : material for material in Material.objects.all()}
    except Exception as e:
        errors.append(f"批量查询失败: {str(e)} ")
    
    existCnt = 0
    to_create = []

    for idx, item in enumerate(payload):
        try:
            if item.material_number in existing_parts:
                existCnt += 1
                continue
            material_obj = existing_materials.get(item.material_number)
            if not material_obj:
                errors.append(f"{idx+1}: 物料 {item.material_name} {item.material_number} 不存在 ")
                faileds.append({'id': idx, 'status': False, })
                continue

            item_dic = {'material': material_obj, 'status': '新建',
                'quantity': to_decimal(item.quantity), 'description': item.description, 'order': order_obj}
            item_dic['plan_delivery'] = datetime.strptime(item.plan_delivery.strip(), day_format).date() if item.plan_delivery else None

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
    item = get_object_or_404(OrderParts, id=item_id)
    return item


@router.get('/order_parts', response=List[OrderPartsOut], url_name='b_jihua/order_parts/list')
@paginate
def list_items(request):
    qs = OrderParts.objects.all()
    return qs


@router.put('/order_parts/{item_id}', response=OrderPartsOut, url_name='b_jihua/order_parts/update')
def update(request, item_id, payload: OrderPartsUpdateIn):
    item = get_object_or_404(OrderParts, id=item_id)
    for attr, value in payload.dict().items():
        if attr in ['plan_delivery', 'deadline'] and value is not None:
            value = datetime.strptime(value.strip(),day_format_s).date() if value else None
        elif attr in ['quantity', 'defectives', 'deliveries', 'cost'] and value is not None:
            value = to_decimal(value) if value else None
        elif attr == 'order':
            order_obj = get_object_or_404(Order, order_id=value)
            value = order_obj
        elif attr == 'material':
            material_obj = get_object_or_404(Material, number=value.split()[-1])
            value = material_obj
        setattr(item, attr, value)
    item.save()
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