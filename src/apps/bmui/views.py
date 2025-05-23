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
def get_versions(request):
    """
    根据 material.id 获取对应的版本列表
    """
    if request.method == "GET":
        material_id = request.GET.get("material_id")
        if not material_id:
            return JsonResponse({"success": False, "message": "缺少 material_id 参数"}, status=400)

        # 查询对应的版本列表
        versions = MaterialVersion.objects.filter(BaseMaterial_id=material_id).values("Version")
        version_list = [v["Version"] for v in versions]

        return JsonResponse({"success": True, "versions": version_list})

    return JsonResponse({"success": False, "message": "无效的请求方法"}, status=405)

@csrf_exempt
def get_parent_materials(request):
    """
    根据 MaterialGroup 的 Name 和 SubName 过滤 parent_material 列表
    """
    if request.method == "GET":
        group_name = request.GET.get("group_name")
        sub_name = request.GET.get("sub_name")
        material = request.GET.get("material")

        if group_name == "None" or group_name == "null":
            return JsonResponse({"success": False, "message": "缺少 group_name 参数"}, status=400)
        if sub_name == "None" or sub_name == "null": 
            subNames = MaterialGroup.objects.filter(Name=group_name).values("SubName")            
            V_list = [{"value": m["SubName"], "text": m["SubName"]} for m in subNames]
        elif material == "None" or material == "null":
            # 根据 group_name 和 sub_name 过滤 BaseMaterial
            materials = BaseMaterial.objects.filter(
                Group__Name=group_name,
                Group__SubName=sub_name
            ).values("Id", "Name")            
            V_list = [{"value": m["Id"], "text": m["Name"]} for m in materials]
        else:
            material = BaseMaterial.objects.get(Id=material)
            versions = MaterialVersion.objects.filter(BaseMaterial=material).values("Version")
            V_list = [{"value": m["Version"], "text": m["Version"]} for m in versions]


        return JsonResponse({"success": True, "selectV": V_list})

    return JsonResponse({"success": False, "message": "无效的请求方法"}, status=405)

@csrf_exempt
def save_boms(request):
    """
    从 payload 中获取 boms 列表数据，并与数据库中已有数据进行比较，
    插入不存在的数据并更新已有数据到 Attribute、MaterialGroup、BaseMaterial、MaterialVersion、Material 和 BOM 表。
    """
    if request.method == "POST":
        try:
            payload = json.loads(request.body)
            boms = payload.get("boms", [])
            parent_material = payload.get("parent_material", None)
            parent_version = payload.get("parent_version", None)

            if not boms:
                return JsonResponse({"success": False, "message": "BOM 数据为空"}, status=400)

            # 使用事务保证数据一致性
            with transaction.atomic():
                # 使用 zip 解压 boms 列表
                bm_ids, bm_names, bm_models, m_helpcode, m_figures,  m_quantits, group_names, group_subNames, m_sources, m_types, m_versions, m_descrs = zip(*boms)

                # 处理 MaterialGroup 表
                material_groups = {
                    (name, sub_name): upsert_model(
                        MaterialGroup,
                        defaults={"SubName": sub_name},
                        Name=name,
                        SubName=sub_name)[0]
                    for name, sub_name in zip(group_names, group_subNames)
                }

                # 处理 Attribute 表
                attributes = {
                    attr_name: upsert_model(
                        Attribute,
                        defaults={"Description": description},
                        Name=attr_name)[0]
                    for attr_name, description in zip(
                        m_sources + m_types, ["获取方式"] * len(m_sources) + ["物料分类"] * len(m_types)
                    ) if attr_name
                }

                # 处理 BaseMaterial 表
                base_materials = {
                    bm_id: upsert_model(
                        BaseMaterial,
                        defaults={
                            "Name": bm_name,
                            "Model": bm_model,                            
                            "HelpCode": helpcode,
                            "Group": material_groups.get((group_name, group_subName))
                        },
                        Id=bm_id)[0]
                    for bm_id, bm_name, bm_model, group_name, group_subName, helpcode in zip(bm_ids, bm_names, bm_models, group_names, group_subNames, m_helpcode)
                }

                # 处理 MaterialVersion 表
                material_versions = {
                    (bm_id, version): upsert_model(
                        MaterialVersion,
                        defaults={},
                        BaseMaterial=base_materials.get(bm_id),
                        Version=version)[0]
                    for bm_id, version in zip(bm_ids, m_versions)
                }

                # 处理 Material 表
                materials = {
                    (bm_id, version): upsert_model(
                        Material,
                        defaults={
                            "Figure": m_figure,
                            "Source": attributes.get(source),
                            "Type": attributes.get(m_type),
                            "Description": descr
                        },
                        MaterialVersion=material_versions.get((bm_id, version))
                    )[0]
                    for bm_id, m_figure, source, m_type, version, descr in zip(
                        bm_ids, m_figures, m_sources, m_types, m_versions, m_descrs)
                }

                # 处理 BOM 表
                
                parent_material_ins = get_bom_by_material(payload)
 
                for child_id, quantity, version in zip(bm_ids, m_quantits, m_versions):
                    child_material = materials.get((child_id, version))
                    if child_material:
                        upsert_model(
                            BOM,
                            defaults={"Quantity": quantity, "Version": version},
                            ParentMaterial=parent_material_ins,
                            ChildMaterial=child_material)

            return JsonResponse({"success": True, "message": "BOM 数据保存成功"})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "无效的 JSON 格式"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "无效的请求方法"}, status=405)

def get_bom_by_material(payload):
    """
    根据 parent_material 的物料编号和版本从 BOM 表获取数据
    """
    material_id = payload.get("parent_material", None)
    version = payload.get("parent_version", None)

    if not material_id or not version:
        return None

    try:
        # 获取对应的 MaterialVersion 对象
        material_version = MaterialVersion.objects.get(
            BaseMaterial__Id=material_id,
            Version=version
        )

        # 获取对应的 Material 对象
        parent_material = Material.objects.get(MaterialVersion=material_version)

        return parent_material  # 返回单个 Material 对象
    except MaterialVersion.DoesNotExist:
        print(f"MaterialVersion 不存在: {material_id}, {version}")
        return None
    except Material.DoesNotExist:
        print(f"Material 不存在: {material_id}, {version}")
        return None

def get_bom_by_parent_material(payload):
    """
    根据 parent_material 的物料编号和版本从 BOM 表获取数据
    """
    material_id = payload.get("parent_material", None)
    version = payload.get("parent_version", None)

    if not material_id or not version:
        return None

    try:
        # 查询 BOM 表，直接通过关联字段过滤
        bom_entries = BOM.objects.filter(
            ParentMaterial__MaterialVersion__BaseMaterial__Id=material_id,
            ParentMaterial__MaterialVersion__Version=version
        ).select_related(
            "ParentMaterial__MaterialVersion__BaseMaterial",
            "ChildMaterial__MaterialVersion__BaseMaterial"
        )

        return bom_entries
    except Exception as e:
        print(f"查询 BOM 数据时发生错误: {e}")
        return None

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