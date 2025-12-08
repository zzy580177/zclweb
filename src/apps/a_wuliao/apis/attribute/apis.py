from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from django_starter.http.response import responses

from apps.a_wuliao.models import *
from apps.a_wuliao.apis.attribute.schemas import *

router = Router(tags=['attribute'])


@router.post('/attribute', url_name='a_wuliao/attribute/create')
def create(request, payload: list[AttributeIn]):
    success = []
    faileds = []
    errors = []
    for idx, item in enumerate(payload):
        try:
            obj,created = Attribute.objects.update_or_create(**item.dict())
            success.append({
                        'id': idx, 'created': created, 'name': obj.name})
        except Exception as e:
            faileds.append({'id': idx})
            errors.append(str(e))
    data = {'faileds': faileds, 'success': success, 'Error': errors}
    if(len(errors) > 0):
        data['message']=f'{len(success)}条记录上传成功, {len(faileds)}条记录上传失败'
        return {'success':False, 'data': data}
    return {'success':True, 'data':{'message': f'成功上传{len(success)}条记录'}}


@router.get('/attribute/{item_id}', response=AttributeOut, url_name='a_wuliao/attribute/retrieve')
def retrieve(request, item_id):
    item = get_object_or_404(Attribute, attribute_id=item_id)
    return item


@router.get('/attribute', response=List[AttributeOut], url_name='a_wuliao/attribute/list')
@paginate
def list_items(request):
    qs = Attribute.objects.all()
    return qs


@router.put('/attribute/{item_id}', response=AttributeOut, url_name='a_wuliao/attribute/update')
def update(request, item_id, payload: AttributeIn):
    item = get_object_or_404(Attribute, attribute_id=item_id)
    for attr, value in payload.dict().items():
        setattr(item, attr, value)
    item.save()
    return item


@router.patch('/attribute/{item_id}', response=AttributeOut, url_name='a_wuliao/attribute/partial_update')
def partial_update(request, item_id, payload: AttributeIn):
    item = get_object_or_404(Attribute, attribute_id=item_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(item, attr, value)
    item.save()
    return item


@router.delete('/attribute/{item_id}', url_name='a_wuliao/attribute/destroy')
def destroy(request, item_id):
    item = get_object_or_404(Attribute, attribute_id=item_id)
    item.delete()
    return responses.ok('已删除')
