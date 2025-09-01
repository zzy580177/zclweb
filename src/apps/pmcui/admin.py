from django.contrib import admin
from django_starter.contrib.admin.tags import html_tags
from django.template.response import TemplateResponse
from django.urls import path
from django.http import JsonResponse
from django.shortcuts import redirect
from .models import *
from apps.bmui.models import Material
import json
from django.db.models import F,Q
from django.db import transaction
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import *
from apps.bmui.models import Attribute
from django.contrib import messages
from django_starter.lib.common import *

from django.core.exceptions import ValidationError

from decimal import Decimal

def to_decimal(val):
    return Decimal(val) if val not in [None, ''] else None

@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = ['Id', 'Name', 'EqpType', 'HCost', 'UCost', 'Description']
    list_filter = ['EqpType']
    change_list_template = "pmcui/step_change_list.html"
    actions = ['delete_selected']
    tableHead = ['工序名','工序类别', '工序计时单价/元','工序计件单价/元','备注']
    tabletype = [
            {'type':'text','name':'Name[]','required': 'required'},
            {'type':'select','name':'EqpType[]','required': 'required'},
            {'type':'number','name':'HCost[]','required': ''},
            {'type':'number','name':'UCost[]','required': ''},
            {'type':'text','name':'Description[]', 'required': ''}]
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}        
        extra_context['tableHead'] = self.tableHead        
        extra_context['tabletype'] = self.tabletype        
        extra_context['tabletype'][1]['options'] = list(Attribute.objects.filter(Description='工序分类').values('Id', 'Name'))
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
           path('addlist/', self.admin_site.admin_view(self.addlist_view), name='pmcui_step_addlist'),
        ]
        return custom_urls + urls
    def add_view(self, request, form_url='', extra_context=None):
        if request.method == "POST":
            result = {}
            try:
                for each in self.tabletype:
                    key = each['name'] 
                    result[key] = request.POST.getlist(each['name'])  
                if not result['Name[]'] or not result['EqpType[]'] :
                    self.message_user(request, "提交的数据不完整，请检查后重试！", level="error")
                    return self.changelist_view(request)

                for Name, EqpType, HCost, UCost, Description in zip(
                    result['Name[]'], result['EqpType[]'], result['HCost[]'], result['UCost[]'], result['Description[]']):
                    if Name.strip():
                        Step.objects.update_or_create(
                            Name=Name,
                            EqpType_id=EqpType,  # 确保是id
                            defaults={
                                'HCost': Decimal(HCost) if HCost else None,
                                'UCost': Decimal(UCost) if UCost else None,
                                'Description': Description
                            }
                        )                # 显示成功消息
                self.message_user(request, "Attribute 填报成功！", level="success")

            except Exception as e:
                # 捕获异常并显示错误消息
                self.message_user(request, f"发生错误：{str(e)}", level="error")

            # 返回到列表页面
            return self.changelist_view(request)

        return super().add_view(request, form_url, extra_context)

    def addlist_view(self, request, form_url='', extra_context=None):
        msg = ''
        if request.method == "POST":
            try:
                payload = json.loads(request.body)
                steps = payload.get("steps", [])
                if not steps:
                    return JsonResponse({"success": False, "message": "step 数据为空"}, status=400)
 
                with transaction.atomic():
                    Names, Eqptypes, UCosts, HCosts, Descriptions = zip(*steps)
                    if not Names and not Eqptypes:
                        self.message_user(request, "提交的数据不完整，请检查后重试！", level="error")
                        return self.changelist_view(request)
                    for Name, Eqptype, UCost, HCost, Description in zip(Names, Eqptypes, UCosts, HCosts, Descriptions):
                        if Name.strip() and Eqptype.strip():
                            Eqptype_attribute = Attribute.objects.get(
                                Name=Eqptype, Description='工序分类')
                        Step.objects.update_or_create(Name = Name, EqpType_id=Eqptype_attribute.Id, defaults={
                                'UCost': Decimal(UCost) if UCost else None, 'HCost': Decimal(HCost) if HCost else None, 
                                'Description': Description if Description else None})
                    return JsonResponse({"success": True, "message": "Step 数据保存成功" + msg})

            except Exception as e:
                return JsonResponse({"success": False, "message": str(e)}, status=500)

@admin.register(ProcessStep)
class ProcessStepAdmin(admin.ModelAdmin):
    list_display = ['PFId', 'display_Steps', 'Route', 'Parameters', 'SeqNum', 'Description']
    list_filter = ['Steps', 'Route']
    #change_list_template = "pmcui/processstep_change_list.html"
    actions = ['delete_selected']

    def display_Steps(self, obj):
        return ", ".join([x for x in obj.Steps.all()])
    display_Steps.short_description = '工序列表'

@admin.register(ProcessRoute)
class ProcessRouteAdmin(admin.ModelAdmin):
    list_display = ['Id', 'Product_id', 'ApprovalStatus', 'Version', 'StartDay', 'Description']
    list_filter = ['Product_id', 'ApprovalStatus']
    #change_list_template = "pmcui/processroute_change_list.html"
    actions = ['delete_selected']
    def get_change_list_template(self, request):
        if request.user.is_superuser:
            return "pmcui/partsorder_change_list_super.html"
        return "pmcui/partsorder_change_list.html"
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        if request.method == "POST":
            return super().changelist_view(request, extra_context=extra_context)
        elif request.method == "GET":
            return super().changelist_view(request, extra_context=extra_context)

        return super().changelist_view(request, extra_context=extra_context)


class PartFilter(admin.SimpleListFilter):
    title = _('子分类')
    parameter_name = 'Part'

    def lookups(self, request, model_admin):
        # 根据主分类动态返回子分类选项
        porder = request.GET.get('POrder__OrderId__exact')
        if porder :
            parts = PartsOrder.objects.filter(
                POrder_id=porder).values_list('Part_id', 'Part__FName').distinct()
            return [(code, str(code) + "-" + name) for code, name in parts if code and name]
        return []

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(Part_id=self.value())
        return queryset

@admin.register(PartsOrder)
class PartsOrderAdmin(admin.ModelAdmin):
    list_display = ['Part', 'Status']
    list_filter = ['POrder', PartFilter]
    partsHead = ['物料编号','数量','备注']
    change_list_template = "pmcui/partsorder_change_list.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}        
        extra_context['partsHead'] = self.partsHead
        data = request.GET.get('POrder')
        extra_context['POrder'] = data if data else ''
        qs = Attribute.objects.filter(Description="工序分类").values('Name', 'Id').distinct()
        extra_context['StepGroup'] = [{'label':data['Name'], 'value' :data['Id']} for data in qs]
        if request.method == "POST":
            return super().changelist_view(request, extra_context=extra_context)
        elif request.method == "GET":
            if (request.GET.get('p')):
                p =  request.GET.get('p')
            return super().changelist_view(request, extra_context=extra_context)
 
@admin.register(MaterialParm)
class MaterialParmAdmin(admin.ModelAdmin):
    list_display = ['Material', 'Size', 'Stuff', 'Surface', 'Cost', 'Description']

    change_list_template = "pmcui/materialParm_change_list.html"
    actions = ['delete_selected']
    tableHead = ['物料', '材料', '加工要求', '表面处理', '成本', '备注']
    FastTabHead = ['物料编号', '物料名', '规格型号', '材料', '加工要求', '表面处理', '成本', '备注']
    tabletype = [
            {'type':'text','name':'Material[]','required': 'required'},
            {'type':'text','name':'Size[]','required': 'required'},
            {'type':'text','name':'Stuff[]','required': ''},
            {'type':'text','name':'Surface[]','required': ''},
            {'type':'number','name':'Cost[]','required': ''},
            {'type':'text','name':'Description[]', 'required': ''}]
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}        
        extra_context['tableHead'] = self.tableHead        
        extra_context['tabletype'] = self.tabletype        
        extra_context['FastTabHead'] = self.FastTabHead
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
           path('addlist/', self.admin_site.admin_view(self.addlist_view), name='pmcui_materialparm_addlist'),
        ]
        return custom_urls + urls
    def add_view(self, request, form_url='', extra_context=None):
        if request.method == "POST":
            result = {}
            try:
                for each in self.tabletype:
                    key = each['name'] 
                    result[key] = request.POST.getlist(each['name'])  

                for Part, Size, Stuff, Surface, Cost, Description in zip(
                    result['Material[]'], result['Size[]'], result['Stuff[]'], result['Surface[]'], result['Cost[]'], result['Description[]']):
                    if Material.strip():
                        MaterialObj = Material.objects.filter(FNumber=Part).first()
                        if not MaterialObj:
                            msg = (f"/r/n未找到物料: {Part}, 请先添加物料")
                            self.message_user(request,  f"发生错误：{msg}", level="error")
                            return super().changelist_view(request, extra_context = extra_context)
                        MaterialParm.objects.update_or_create(
                            Material_id=MaterialObj.FId,
                            defaults={
                                'Size': Size if Size else None,
                                'Stuff': Stuff if Stuff else None,
                                'Surface': Surface if Surface else None,
                                'Cost': Decimal(Cost) if Cost else None,
                                'Description': Description})
                # 显示成功消息
                self.message_user(request, "Attribute 填报成功！", level="success")

            except Exception as e:
                # 捕获异常并显示错误消息
                self.message_user(request, f"发生错误：{str(e)}", level="error")

            # 返回到列表页面
            return self.changelist_view(request)

        return super().add_view(request, form_url, extra_context)

    def addlist_view(self, request, form_url='', extra_context=None):
        msg = ''
        if request.method == "POST":
            try:
                payload = json.loads(request.body)
                parms = payload.get("parms", [])
                if not parms:
                    return JsonResponse({"success": False, "message": "step 数据为空"}, status=400)
 
                with transaction.atomic():
                    FNumbers, FNames, FModels, Stuffs, Sizes, Surfaces, Costs, Descriptions = zip(*parms)
                    for FNumber, FName, FModel, Stuff, Size, Surface, Cost, Description in zip(FNumbers, FNames, FModels, Stuffs, Sizes, Surfaces, Costs, Descriptions):
                        if FNumber.strip() or FName.strip() or FModel.strip():
                            filters = Q()
                            if FNumber:
                                filters &= Q(FNumber=FNumber)
                            if FName:
                                filters &= Q(FName=FName)
                            if FModel:
                                filters &= Q(FModel=FModel)
                            partObj = Material.objects.filter(filters).first()
                        if not partObj:
                            msg = (f"未找到物料: {FNumber} {FName} {FModel} 请先添加物料")
                            return JsonResponse({"success": False, "message": msg}, status=500)
                        MaterialParm.objects.update_or_create(
                            Material_id=partObj.FId,
                            defaults={
                                'Size': Size if Size else None,
                                'Stuff': Stuff if Stuff else None,
                                'Surface': Surface if Surface else None,
                                'Cost': Decimal(Cost) if Cost else None,
                                'Description': Description})
                    return JsonResponse({"success": True, "message": "Step 数据保存成功" + msg})

            except Exception as e:
                return JsonResponse({"success": False, "message": str(e)}, status=500)
