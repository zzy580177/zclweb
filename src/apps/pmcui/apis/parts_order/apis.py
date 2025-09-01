from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate, PageNumberPagination

from django_starter.http.response import responses

from apps.pmcui.models import *
from apps.pmcui.apis.parts_order.schemas import *
from apps.bmui.models import Material

from django.db.models import Q, F
from django.db import transaction

router = Router(tags=['parts'])

class SuccessResponse(Schema):
    success: bool
    message: str


class TenPerPagePagination(PageNumberPagination):
    page_size = 20

@router.post('/create',  url_name='pmcui/parts_order/create')
def create(request, payload: List[PartsOrderIn]):
    success = []
    faileds = []
    errors = []
    with transaction.atomic():
        for idx, item in enumerate(payload):
            try:
                part = Material.objects.filter(FNumber=item.FNumber).first()
                if not part :
                    errors.append(f"idex {idx+1}: 未找到物料号 {item.FNumber} ")
                    faileds.append({'id': idx, 'status': False, 'Cause': 'not_found', 'key': 'FNumber'})
                    continue
                obj, created = PartsOrder.objects.update_or_create(
                    POrder_id=item.POrder_id,
                    Part__FNumber=item.FNumber,
                    defaults={
                        'Status': item.Status,
                        'Quantity': item.Quantity,
                        'Description': item.Description
                    }
                )
                success.append({
                        'id': idx, 'created': created, 'part_number': obj.Part.FNumber})
            except Exception as e:
                errors.append(f"idex {idx+1}: {str(e)} ")
                faileds.append({'id': idx, 'status': False, 'Cause': 'Exception', 'key': ''})
                continue
    data = {'faileds': faileds, 'success': success, 'Error': errors}
    if(len(errors) > 0):
        data['message']=f'{len(success)}条记录上传成功, {len(faileds)}条记录上传失败'
        return {'success':False, 'data': data}
    return {'success':True, 'data':{'message': f'成功上传{len(success)}条记录'}}

@router.put('/update/{item_id}', url_name='pmcui/parts_order/update')
def update(request, item_id, payload: PartsOrderIn):
    try:
        item = get_object_or_404(PartsOrder.objects, POrder_id=payload.POrder_id, Part_id=payload.FId)
        if (not item):
            return {'success':False, 'message':'更新对象未找到'}   
        for attr, value in payload.dict().items():
            if attr in [ 'Status', 'Quantity', 'Description']:
                setattr(item, attr, value)
        item.save()
        return {'success':True, 'data': {'message':'更新成功'}}
    except Exception as e:
        return {'success':False, 'data':{'message':{str(e)}}}  

@router.get('/parts_order/{item_id}', response=PartsOrderOut, url_name='pmcui/parts_order/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(PartsOrder, Id=item_id)
    return item


@router.get('/parts_order', response=List[PartsOrderOut], url_name='pmcui/parts_order/list')
@paginate
def list_items(request):
    qs = PartsOrder.objects.all()
    return qs

@router.get('/parts_list_by_order', response=List[PartsOrderOut2], url_name='pmcui/parts_order/list_by_orderid')
@paginate(TenPerPagePagination)
def list_by_orderid(request, OrderId: str = None, FId: int = None, FNumber: str = None):
    from django.db.models import Prefetch
    
    qs = PartsOrder.objects.select_related('Part','Part__FParent').prefetch_related(
        Prefetch('Part__parents',queryset=Material.objects.select_related('FUnit'),
            to_attr='sub_parts'))    
    filters = Q()
    if OrderId:
        filters &= Q(POrder_id=OrderId)
    if FId:
        filters &= Q(Part_id=FId)
    if FNumber:
        filters &= Q(Part__FNumber__icontains=FNumber)
    if filters:
        qs = qs.filter(filters).order_by('-Id')
    return qs




@router.patch('/parts_order/{item_id}', response=PartsOrderOut, url_name='pmcui/parts_order/partial_update')
def partial_update(request, item_id, payload: PartsOrderIn):
    item = get_object_or_404(PartsOrder, id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/parts_order/{item_id}', url_name='pmcui/parts_order/destroy')
def destroy(request, item_id):
    item = get_object_or_404(PartsOrder, id=item_id)
    item.delete()
    return responses.ok('已删除')

@router.post('/admin_update',  url_name='pmcui/parts_order/admin_update')
def admin_update(request, payload: PartsOrderAdminIn):
    try:
        item = PartsOrder.objects.prefetch_related('Part', 'POrder').filter(
                Q(POrder_id=payload.POrder_id, Part__FNumber=payload.Part_FNumber)).first()
        if (not item): return responses.not_found("目标数据不存在")
        if item.Quantity != payload.Quantity or item.Description != payload.Description:
            item.Quantity = payload.Quantity
            item.Description = payload.Description
            if item.Status == '未就緒':
                item.Status = '已变更'
                item.POrder.Status = '已变更'
                item.POrder.save()
            item.save()
        return responses.ok("更新成功")
    except Exception as e:
        responses.error(f"{str(e)}")

@router.post('/admin_create', url_name='pmcui/parts_order/admin_create')
def admin_create(request, payload: list[PartNumOrderAdminIn]):
    created_orders = []
    errors = []
    with transaction.atomic():
        for idx, item in enumerate(payload):
            try:
                main_keys = {}
                defaults = {}
                for attr, value in item.dict(exclude_unset=True).items():
                    if attr.startswith('Part_'):
                        material = Material.objects.filter(Q(FNumber=value)).first()
                        if not material:
                            errors.append(f"Row {idx}: Material {value} not found")
                            continue
                        main_keys['Part_id'] = material.FId
                    elif attr.startswith('POrder'):
                        main_keys[attr] = value
                    else:
                        defaults[attr] = value
                
                if main_keys:
                    obj, created = PartsOrder.objects.update_or_create(
                        **main_keys, defaults=defaults)
                    created_orders.append({
                        'id': idx, 'created': created, 'part_number': obj.Part.FNumber})
            
            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")
                continue
    
    results = {'created_count': len(created_orders), 'results': created_orders}
    if errors:
        return responses.error("成功更新{len(created_orders)}条记录，失败{len(errors)条记录}", 
                               {'success': False, 'errors': errors, 'results': results})
    
    return responses.ok("成功更新{len(created_orders)}条记录", {'success': True, 'results': results })
