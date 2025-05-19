from django.contrib import admin
from django_starter.contrib.admin.tags import html_tags
from django.template.response import TemplateResponse
from django.urls import path
from django.http import JsonResponse
from django.shortcuts import redirect
from .models import *

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ['Id', 'Name', 'Description']
    change_list_template = "bmui/attribute_change_list.html"
    actions = ['delete_selected_attributes']  # 添加自定义动作

    def changelist_view(self, request, extra_context=None):
        # 定义 Description 的选项
        description_options = ["物料分类", "物料属性", "获取方式"]

        # 传递到模板的上下文
        extra_context = extra_context or {}
        extra_context['description_options'] = description_options

        return super().changelist_view(request, extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        if request.method == "POST":
            try:
                # 获取表单数据
                descriptions = request.POST.getlist("description[]")
                names = request.POST.getlist("name[]")

                # 检查表单数据是否完整
                if not descriptions or not names:
                    self.message_user(request, "提交的数据不完整，请检查后重试！", level="error")
                    return self.changelist_view(request)

                # 遍历提交的名称列表，逐一检查并保存到数据库
                for description, name in zip(descriptions, names):
                    if name.strip():  # 确保名称不为空
                        # 检查是否已存在相同的 Name 和 Description
                        if not Attribute.objects.filter(Name=name, Description=description).exists():
                            Attribute.objects.create(Name=name, Description=description)

                # 显示成功消息
                self.message_user(request, "Attribute 填报成功！", level="success")

            except Exception as e:
                # 捕获异常并显示错误消息
                self.message_user(request, f"发生错误：{str(e)}", level="error")

            # 返回到列表页面
            return self.changelist_view(request)

        return super().add_view(request, form_url, extra_context)

    def delete_selected_attributes(self, request, queryset):
        """自定义动作：删除选中的 Attribute 项"""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"成功删除了 {count} 条 Attribute 项！", level="success")
        return None  # 返回 None 表示操作完成

    delete_selected_attributes.short_description = "删除选中项"

@admin.register(BaseMaterial)
class BaseMaterialAdmin(admin.ModelAdmin):
    list_display = ['Id','Name','Model','CreateTime','UpdateTime','IsDelete','IsActive',]

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['Id','MaterialVersion','Type','Source','Attribute','Figure','Description','CreateTime','UpdateTime','IsDelete','IsActive',]

@admin.register(BOM)
class BOMAdmin(admin.ModelAdmin):
    list_display = ['id', 'ParentMaterial', 'ChildMaterial', 'Quantity', 'Version', 'Description','CreateTime', 'UpdateTime', 'IsDelete', 'IsActive', ]
    change_list_template = "bmui/bom_change_list.html"
    editTableHead = ['物料编号', '物料名称', '物料型号', '助记码','图号', '数量', '物料组别','2级组别', '获取方式', '物料属性', '物料版本', '备注']
    
    def get_urls(self):
        """
        添加自定义 URL 路由
        """
        urls = super().get_urls()
        custom_urls = [
            path('get-parent-materials/', self.admin_site.admin_view(self.get_parent_materials_view), name='bmui_get_parent_materials'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        # 获取父物料、子物料、物料版本和属性数据
        child_materials = Material.objects.filter(IsActive=True, IsDelete=False)
        groups = MaterialGroup.objects.values("Name").distinct()

        # 传递到模板的上下文
        extra_context = extra_context or {}
        extra_context['child_materials'] = child_materials
        extra_context['groups'] = [group["Name"] for group in groups]

        extra_context['editTableHead'] = self.editTableHead

        if request.method == "POST":
            return super().changelist_view(request, extra_context=extra_context)
        elif request.method == "GET":
            return super().changelist_view(request, extra_context=extra_context)

        return super().changelist_view(request, extra_context=extra_context)

    def get_parent_materials_view(self, request):
        """
        根据 MaterialGroup 的 Name 和 SubName 过滤 parent_material 列表，并返回过滤后的 changelist_view
        """
        data = []

        if request.method == "GET":
            group_name = request.GET.get("group_name")
            sub_name = request.GET.get("sub_name")
            material = request.GET.get("material")


            if not group_name or group_name in ["None", "null"]:
                self.message_user(request, "缺少 group_name 参数", level="error")

            elif sub_name in ["None"]:
                # 获取子组名称列表
                sub_names = MaterialGroup.objects.filter(Name=group_name).values("SubName")
                data = [{"value": m["SubName"], "text": m["SubName"] or "无子组"} for m in sub_names]
            elif not material or material in ["None", "null"]:
                # 根据 group_name 和 sub_name 过滤 BaseMaterial
                materials = BaseMaterial.objects.filter(
                    Group__Name=group_name,
                    Group__SubName=sub_name
                ).values("Id", "Name")
                data = [{"value": m["Id"], "text": m["Name"]} for m in materials]
            else:
                # 获取指定 material 的版本列表
                try:
                    material_instance = BaseMaterial.objects.get(Id=material)
                    versions = MaterialVersion.objects.filter(BaseMaterial=material_instance).values("Version")
                    data = [{"value": m["Version"], "text": m["Version"]} for m in versions]
                except BaseMaterial.DoesNotExist:
                    self.message_user(request, "指定的 material 不存在", level="error")
        if data.__len__ == 0:
            return JsonResponse({"success": False, "message": "无效的请求方法"}, status=405)
        else:
            return JsonResponse({"success": True, "selectV": data})

    def add_view(self, request, form_url='', extra_context=None):
        if request.method == "POST":
            parent_material_id = request.POST.get("parent_material")
            child_material_ids = request.POST.getlist("child_material[]")
            quantities = request.POST.getlist("quantity[]")
            version = request.POST.get("version")
            description = request.POST.get("description")

            parent_material = Material.objects.get(pk=parent_material_id)

            for child_material_id, quantity in zip(child_material_ids, quantities):
                child_material = Material.objects.get(pk=child_material_id)
                BOM.objects.create(
                    ParentMaterial=parent_material,
                    ChildMaterial=child_material,
                    Quantity=quantity,
                    Version=version,
                    Description=description,
                )

            self.message_user(request, "BOM 填报成功！")
            return self.changelist_view(request)

        return super().add_view(request, form_url, extra_context)

    def add_parent(self, request):
        if request.method == "POST":
            parent_material_id = request.POST.get("parent_material")
            if not parent_material_id or parent_material_id == "None":
                self.message_user(request, "请选择主产品！", level="error")
                return redirect('admin:bmui_bom_changelist')

            # 处理主产品逻辑
            parent_material = Material.objects.get(pk=parent_material_id)
            self.message_user(request, f"主产品 {parent_material.Name} 已保存！", level="success")
            return redirect('admin:bmui_bom_changelist')

        return JsonResponse({"error": "Invalid request method"}, status=400)

    def add_details(self, request):
        if request.method == "POST":
            child_materials = request.POST.getlist("child_material[]")
            quantities = request.POST.getlist("quantity[]")

            if not child_materials or not quantities:
                self.message_user(request, "请填写零件组件明细！", level="error")
                return redirect('admin:bmui_bom_changelist')

            # 保存零件组件明细逻辑
            for child_material_id, quantity in zip(child_materials, quantities):
                if child_material_id != "None" and quantity:
                    BOM.objects.create(
                        ChildMaterial_id=child_material_id,
                        Quantity=quantity,
                        # 添加其他需要的字段
                    )
            self.message_user(request, "零件组件明细已保存！", level="success")
            return redirect('admin:bmui_bom_changelist')

        return JsonResponse({"error": "Invalid request method"}, status=400)




