from django.contrib import admin
from django_starter.contrib.admin.tags import html_tags
from django.template.response import TemplateResponse
from django.urls import path
from django.http import JsonResponse
from django.shortcuts import redirect
from .models import *
import json
from django.db import transaction
from django.db.models import F

from django.contrib.admin import SimpleListFilter

from django.utils.translation import gettext_lazy as _

def delete_selected(modeladmin, request, queryset):
    count = queryset.count()
    queryset.delete()
    modeladmin.message_user(request, f"成功删除了 {count} 条记录！", level="success")
delete_selected.short_description = "删除选中项"


class GroupFilter(admin.SimpleListFilter):
    title = _('子分类')
    parameter_name = 'GroupCode'

    def lookups(self, request, model_admin):
        # 根据主分类动态返回子分类选项
        primary = request.GET.get('FGroup__FClass__exact')
        if primary :
            group_codes = MaterialGroup.objects.filter(
                FClass=primary,FGroupCode=''
            ).values_list('FNumber', 'FName').distinct()
            return [(code, code + "-" + name) for code, name in group_codes if code and name]
        return []

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(FGroup__FNumber__startswith=self.value())
        return queryset

class SubGroupFilter(admin.SimpleListFilter):
    title = _('子组代码')
    parameter_name = 'SubGroupCode'

    def lookups(self, request, model_admin):
        primary = request.GET.get('GroupCode')
        if primary:
            sub_group_codes = MaterialGroup.objects.filter(
                FGroupCode=primary, FSubGroupCode='' 
            ).values_list('FNumber', 'FName').distinct()

            return [(code, f"{code} - {name}") for code, name in sub_group_codes if code and name]
        return []

    def queryset(self, request, queryset):
        # 根据选定的 GroupCode 过滤数据
        if self.value():
            return queryset.filter(FGroup__FNumber__startswith=self.value())
        return queryset

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ['Id', 'Name', 'Description']
    list_filter = ['Description']
    change_list_template = "bmui/attribute_change_list.html"
    actions = [delete_selected]  # 添加自定义动作

    def changelist_view(self, request, extra_context=None):
        # 定义 Description 的选项
        description_options = ["单位", "获取方式", "工序分类"]

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


@admin.register(MaterialGroup)
class MaterialGroupAdmin(admin.ModelAdmin):
    list_display = ['FId','FName','FParent','FNumber','FLevel', 'get_FClass', 'get_FGroupCode', 'FSubGroupCode']
    list_filter = ['FClass']
    change_list_template = "bmui/materialgroup_change_list.html"
    actions = [delete_selected]  # 添加自定义动作

    def get_FClass(self, obj):
        """显示分类的可读值"""
        return dict(MaterialGroup.FClass_choics).get(obj.FClass, "无")
    get_FClass.short_description = "分类"

    def get_FGroupCode(self, obj):
        """显示组代码的可读值"""
        return dict(MaterialGroup.FGroupCode_choics).get(obj.FGroupCode, "无")
    get_FGroupCode.short_description = "组别"

    tableHead = ['组序号', '组名称', '父组', '组编号', '层级', '分类', '组代码', '子组代码']
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['tableHead'] = self.tableHead

        if request.method == "POST":
            return super().changelist_view(request, extra_context=extra_context)
        elif request.method == "GET":
            return super().changelist_view(request, extra_context=extra_context)

        return super().changelist_view(request, extra_context=extra_context)
    def get_urls(self):
        """
        添加自定义 URL 路由
        """
        urls = super().get_urls()
        custom_urls = [
            path('addlist/', self.admin_site.admin_view(self.addlist_view), name='bmui_materialgroup_addlist'),
        ]
        return custom_urls + urls
    def add_view(self, request, form_url='', extra_context=None):
        if request.method == "POST":
            try:
                # 获取表单数据
                FIds = request.POST.getlist("FId[]")
                FNames = request.POST.getlist("FName[]")
                FNumbers = request.POST.getlist("FNumber[]")

                # 检查表单数据是否完整
                if not FIds or not FNames or not FNumbers:
                    self.message_user(request, "提交的数据不完整，请检查后重试！", level="error")
                    return self.changelist_view(request)

                # 遍历提交的名称列表，逐一检查并保存到数据库
                for FId, FName, FNumber in zip(FIds, FNames, FNumbers):
                    if FId.strip():  # 确保名称不为空
                        # 检查是否已存在相同的 Name 和 Description
                        if not MaterialGroup.objects.filter(FId=FId, FNumber=FNumber).exists():
                            FLevel=FNumber.count('.')
                            FPNumber = FClass= FGroupCode= FSubGroupCode =None
                            if FLevel > 0:
                                FClass=FNumber.split('.')[0]
                                FPNumber=FClass
                            if FLevel > 1:
                                FGroupCode=FNumber.split('.')[0] + '.' +FNumber.split('.')[1]
                                FPNumber=FGroupCode
                            if FLevel > 2:
                                FSubGroupCode=FGroupCode  + '.' + FNumber.split('.')[2]
                                FPNumber=FSubGroupCode
                            if FLevel > 3:
                                FPNumber=FPNumber  + '.' + FNumber.split('.')[3]    
                            FPId=MaterialGroup.objects.get(FNumber=FPNumber).FId if FLevel>0 else None
                            MaterialGroup.objects.create(FId=FId, FNumber=FNumber, FName=FName, FLevel=FLevel, FParent_id=FPId, 
                                                         FClass=FClass, FGroupCode=FGroupCode, FSubGroupCode=FSubGroupCode)
                # 显示成功消息
                self.message_user(request, "Attribute 填报成功！", level="success")

            except Exception as e:
                # 捕获异常并显示错误消息
                self.message_user(request, f"发生错误：{str(e)}", level="error")

            # 返回到列表页面
            return self.changelist_view(request)

        return super().add_view(request, form_url, extra_context)

    def addlist_view(self, request, form_url='', extra_context=None):
        if request.method == "POST":
            try:
                payload = json.loads(request.body)
                materialgroups = payload.get("materialgroups", [])

                if not materialgroups:
                    return JsonResponse({"success": False, "message": "materialgroup 数据为空"}, status=400)

                with transaction.atomic():
                    FIds, FNames, FPIds, FNumbers, FLevels,  FClasses, FGroups, FSubGroups = zip(*materialgroups)
                    if not FIds or not FNames or not FNumbers:
                        self.message_user(request, "提交的数据不完整，请检查后重试！", level="error")
                        return self.changelist_view(request)

                    for FId, FName, FPId, FNumber, FLevel, FClass, FGroup, FSubGroup in zip(FIds, FNames, FPIds, FNumbers, FLevels,  FClasses, FGroups, FSubGroups):
                        if FId.strip():
                            MaterialGroup.objects.update_or_create(FId=FId, FNumber=FNumber, FName=FName, FLevel=FLevel, FParent_id=FPId, 
                                FClass=FClass, FGroupCode=FGroup, FSubGroupCode=FSubGroup)
                return JsonResponse({"success": True, "message": "BOM 数据保存成功"})

            except Exception as e:
                return JsonResponse({"success": False, "message": str(e)}, status=500)



@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['FId','FName','FGroup','FNumber','FHelpCode', 'FModel', 'FUnit', 'FSource','FDescription']
    list_filter = ['FGroup__FClass', GroupFilter, SubGroupFilter]
    actions = [delete_selected]  # 添加自定义动作
    class Media:
        js = ('js/filter_chain.js',)
    
    change_list_template = "bmui/material_change_list.html"


    tableHead = ['物料序号','物料名称','物料组','物料编号','助记码', '型号', '单位', '来源','备注']
    tabletype = [
            {'type':'number','name':'FId[]','required': 'required'},{'type':'text','name':'FName[]','required': 'required'},
            {'type':'select','name':'FGroup[]','required': 'required'},     
            {'type':'text','name':'FNumber[]','required': 'required'},
            {'type':'text','name':'FHelpCode[]','required': ''}, {'type':'text','name':'FModel[]','required': ''}, 
            {'type':'select', 'name':'FUnit[]', 'required': 'required'},           
            {'type':'text','name':'FSource[]','required': ''}, {'type':'text','name':'FDescription[]','required': ''}]
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['tableHead'] = self.tableHead        
        extra_context['tabletype'] = self.tabletype
        extra_context['tabletype'][2]['options'] = list(MaterialGroup.objects.values(Id=F('FId'), Name=F('FName')))
        extra_context['tabletype'][6]['options'] = list(Attribute.objects.filter(Description='单位').values('Id', 'Name'))
        if request.method == "POST":
            return super().changelist_view(request, extra_context=extra_context)
        elif request.method == "GET":
            return super().changelist_view(request, extra_context=extra_context)

        return super().changelist_view(request, extra_context=extra_context)
    def get_urls(self):
        """
        添加自定义 URL 路由
        """
        urls = super().get_urls()
        custom_urls = [
            path('getgroup/', self.admin_site.admin_view(self.getgroup_view), name='bmui_material_getgroup'),
            path('addlist/', self.admin_site.admin_view(self.addlist_view), name='bmui_material_addlist'),
        ]
        return custom_urls + urls
    def add_view(self, request, form_url='', extra_context=None):
        if request.method == "POST":
            result = {}
            try:
                for each in self.tabletype:
                    key = each['name'] 
                    result[key] = request.POST.getlist(each['name'])  
                if not result['FId[]'] or not result['FName[]'] or not result['FNumber[]']:
                    self.message_user(request, "提交的数据不完整，请检查后重试！", level="error")
                    return self.changelist_view(request)

                for FId, FName, FGroup, FNumber, FHelpCode,  FModel, FUnit, FSource, FDescription in zip(
                    result['FId[]'], result['FName[]'], result['FGroup[]'], result['FNumber[]'], result['FHelpCode[]'],
                    result['FModel[]'], result['FUnit[]'], result['FSource[]'], result['FDescription[]']):
                    if FId.strip():
                        Material.objects.update_or_create(FId=FId, FNumber=FNumber, defaults={
                            'FName': FName,'FHelpCode': FHelpCode,'FModel': FModel, 'FUnit_id': FUnit,
                            'FSource': FSource, 'FDescription': FDescription, 'FGroup_id': FGroup})
                # 显示成功消息
                self.message_user(request, "Attribute 填报成功！", level="success")

            except Exception as e:
                # 捕获异常并显示错误消息
                self.message_user(request, f"发生错误：{str(e)}", level="error")

            # 返回到列表页面
            return self.changelist_view(request)

        return super().add_view(request, form_url, extra_context)

    def addlist_view(self, request, form_url='', extra_context=None):
        if request.method == "POST":
            try:
                payload = json.loads(request.body)
                materials = payload.get("materials", [])

                if not materials:
                    return JsonResponse({"success": False, "message": "material 数据为空"}, status=400)

                with transaction.atomic():
                    # 提取所有需要的 FGroup 和 FUnit 名称
                    FGroupIds = set(row[2] for row in materials)
                    FUnits = set(row[6] for row in materials)

                    # 批量获取所有相关的 MaterialGroup 和 Attribute
                    group_objs = MaterialGroup.objects.filter(FId__in=FGroupIds)
                    group_map = {str(obj.FId): obj for obj in group_objs}

                    unit_objs = Attribute.objects.filter(Name__in=FUnits, Description='单位')
                    unit_map = {obj.Name: obj for obj in unit_objs}

                    # 检查是否需要新建 MaterialGroup
                    missing_groups = FGroupIds - set(group_map.keys())
                    
                    # 需要新建的单位
                    missing_units = FUnits - set(unit_map.keys())
                    new_units = [Attribute(Name=name, Description='单位') for name in missing_units if name.strip()]
                    Attribute.objects.bulk_create(new_units)
                    # 更新 unit_map
                    if new_units:
                        for obj in Attribute.objects.filter(Name__in=missing_units, Description='单位'):
                            unit_map[obj.Name] = obj

                    # 批量 upsert Material
                    for FId, FName, FGroup, FNumber, FHelpCode, FModel, FUnit, FSource, FDescription in materials:
                        if FId.strip() and FUnit.strip():
                            group_obj = group_map.get(str(FGroup))
                            unit_obj = unit_map.get(FUnit)
                            if not group_obj or not unit_obj:
                                msg = (f"/r/n未找到物料组: {FGroup}, 请先添加物料组")
                                return JsonResponse({"success": False, "message": msg}, status=500)
                            Material.objects.update_or_create(
                                FId=FId, FNumber=FNumber,
                                defaults={
                                    'FName': FName,
                                    'FHelpCode': FHelpCode,
                                    'FModel': FModel,
                                    'FGroup': group_obj,
                                    'FUnit': unit_obj,
                                    'FSource': FSource,
                                    'FDescription': FDescription
                                }
                            )
                return JsonResponse({"success": True, "message": "BOM 数据保存成功"})

            except Exception as e:
                return JsonResponse({"success": False, "message": str(e)}, status=500)
        
    def getgroup_view(self, request):
        fclass = request.GET.get('FClass')
        if not fclass:
            return JsonResponse([], safe=False)

        group_codes = MaterialGroup.objects.filter(
            FGroupCode=fclass, FSubGroupCode='' 
        ).values_list('FNumber', 'FName').distinct()
        return JsonResponse(list(group_codes), safe=False)    



