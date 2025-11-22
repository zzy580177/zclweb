from typing import Any, Mapping
import decimal

import orjson
from django.conf import settings
from django.http import HttpRequest
from ninja import NinjaAPI, Swagger
from ninja.renderers import JSONRenderer, BaseRenderer
from django_starter.apis import router
from apps.account.apis import router as account_router
from apps.amfui.apis import router as amfui_router
from apps.a_wuliao.apis import router as a_wuliao_router
from apps.b_jihua.apis import router as b_jihua_router
from apps.c_gongyi.apis import router as c_gongyi_router


def convert_decimal_to_float(obj):
    """递归转换 decimal.Decimal 为 float"""
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal_to_float(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        # 处理对象实例
        return convert_decimal_to_float(obj.__dict__)
    else:
        return obj


class ORJSONRenderer(JSONRenderer):
    def render(self, request: HttpRequest, data: Any, *, response_status: int) -> Any:
        ret = {
            'code': response_status,
            'data': data,
            'success': False
        }

        if isinstance(data, dict):
            ret['message'] = data.pop('detail', '请求成功')

        if 200 <= response_status < 300:
            ret['success'] = True

        # 转换 Decimal 类型为 float
        ret = convert_decimal_to_float(ret)
        
        return orjson.dumps(ret, **self.json_dumps_params)


api = NinjaAPI(
    title=f'{settings.DJANGO_STARTER["project_info"]["name"]} APIs',
    description=settings.DJANGO_STARTER["project_info"]["description"],
    renderer=ORJSONRenderer(),
    urls_namespace='api',
    docs=Swagger(settings={"persistAuthorization": True})
)

api.add_router('django-starter', router)
api.add_router('account', account_router)
api.add_router('amfui', amfui_router)
api.add_router('a_wuliao', a_wuliao_router)
api.add_router('b_jihua', b_jihua_router)
api.add_router('c_gongyi', c_gongyi_router)
