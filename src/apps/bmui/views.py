from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import *
import json

@csrf_exempt
def quick_fill(request):
    if request.method == "POST":
        try:
            # 获取提交的数据
            rows = request.POST.getlist("rows")
            for row in rows:
                FId = row.get("FId")
                FName = row.get("FName")
                FParent = row.get("FParent")
                FNumber = row.get("FNumber")
                FLevel = row.get("FLevel")
                FClass = row.get("FClass")

                # 创建或更新 MaterialGroup
                MaterialGroup.objects.update_or_create(
                    FId=FId,
                    defaults={
                        "FName": FName,
                        "FParent_id": FParent,
                        "FNumber": FNumber,
                        "FLevel": FLevel,
                        "FClass": FClass,
                    }
                )
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "无效的请求方法"})

def get_fgroupcode_options(request):
    fclass = request.GET.get('fclass')
    if fclass:
        options = MaterialGroup.objects.filter(FClass=fclass).values_list('FGroupCode', flat=True).distinct()
        return JsonResponse([{'value': code, 'label': code} for code in options], safe=False)
    return JsonResponse([], safe=False)

def upsert_model(model, defaults=None, **lookup):
    """
    通用的去重插入或更新函数。
    :param model: 模型类
    :param defaults: 默认值字典，用于更新或插入
    :param lookup: 用于查找记录的字段
    :return: (实例, 是否创建)
    """
    defaults = defaults or {}
    obj, created = model.objects.update_or_create(defaults=defaults, **lookup)
    return obj, created




@csrf_exempt
def save_attributes(request):
    """
    从 payload 中获取 attributes 列表数据，并与数据库中已有数据进行比较，
    插入不存在的数据并更新已有数据到 Attribute 表。
    """
    if request.method == "POST":
        try:
            payload = json.loads(request.body)
            attr_names = payload.get("names", [])
            description = payload.get("description", "")

            if not attr_names:
                return JsonResponse({"success": False, "message": "属性数据为空"}, status=400)

            # 使用事务保证数据一致性
            with transaction.atomic():
                for attr_name in attr_names:
                    if not attr_name:
                        return JsonResponse({"success": False, "message": "属性名称不能为空"}, status=400)

                    # 插入或更新 Attribute 表
                    upsert_model(
                        Attribute,
                        defaults={"Description": description},
                        Name=attr_name[0]
                    )

            return JsonResponse({"success": True, "message": "属性数据保存成功"})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "无效的 JSON 格式"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "无效的请求方法"}, status=405)