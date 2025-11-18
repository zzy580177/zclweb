from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.b_jihua.models import *
from apps.b_jihua.apis.order.schemas import *


router = Router(tags=['order'])
from datetime import datetime
day_format = "%Y-%m-%d"
@router.post('/order',  url_name='b_jihua/order/create')
def create(request, payload:List[OrderIn]):
    success = []
    faileds = []
    errors = []
    try:          
        existing_order = {order.pk: order for order in Order.objects.all()}
    except Exception as e:
        errors.append(f"批量查询失败: {str(e)} ")
    existCnt = 0
    to_create = []

    for idx, item in enumerate(payload):
        try:
            item_dic = {k: v for k, v in item.dict().items() if k != 'plan_delivery'}
            item_dic['plan_delivery'] = datetime.strptime(item.plan_delivery.strip(), day_format).date() if item.plan_delivery else None
            item_dic['status'] = '新建'
            if item.order_id in existing_order:
                existCnt += 1
                continue
            to_create.append((idx, item_dic, item.order_id))
        except Exception as e:
            errors.append(f"{idx+1}: 批量查询失败: {str(e)} ")
            faileds.append({'id': idx, 'status': False, })
    if to_create:
        try:
            orders = []
            for idx, item_dic, _ in to_create:
                orders.append(Order(**item_dic))
            Order.objects.bulk_create(orders)
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

@router.get('/order/{item_id}', response=OrderOut, url_name='b_jihua/order/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(Order, id=item_id)
    return item


@router.get('/order', response=List[OrderOut], url_name='b_jihua/order/list')
@paginate
def list_items(request):
    qs = Order.objects.all()
    return qs


@router.put('/order/{item_id}', response=OrderOut, url_name='b_jihua/order/update')
def update(request, item_id, payload: OrderUpdataIn):
    item = get_object_or_404(Order, order_id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/order/{item_id}', response=OrderOut, url_name='b_jihua/order/partial_update')
def partial_update(request, item_id, payload: OrderIn):
    item = get_object_or_404(Order, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/order/{item_id}', url_name='b_jihua/order/destroy')
def destroy(request, item_id):
    item = get_object_or_404(Order, id=item_id)
    item.delete()
    return responses.ok('已删除')