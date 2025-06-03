from django.contrib import admin
from django_starter.contrib.admin.tags import html_tags
from django.template.response import TemplateResponse
from django.urls import path
from django.http import JsonResponse
from django.shortcuts import redirect
from .models import *
from apps.bmui.models import Material
import json
from django.db.models import F
from django.db import transaction
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import *
from apps.bmui.models import Attribute
from django.contrib import messages

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
    list_display = ['PFId', 'Step', 'Route', 'Parameters', 'SeqNum', 'Description']
    list_filter = ['Step', 'Route']
    #change_list_template = "pmcui/processstep_change_list.html"
    actions = ['delete_selected']

@admin.register(ProcessRoute)
class ProcessRouteAdmin(admin.ModelAdmin):
    list_display = ['Id', 'Product_id', 'ApprovalStatus', 'Version', 'StartDay', 'Description']
    list_filter = ['Product_id', 'ApprovalStatus']
    #change_list_template = "pmcui/processroute_change_list.html"
    actions = ['delete_selected']

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
    list_filter = ['POrder', PartFilter]
    partsHead = ['物料编号','数量','备注']
    change_list_template = "pmcui/partsorder_change_list.html"
    def getPartName(self, obj):
        """获取物料名称"""
        return obj.Part.FName if obj.Part else None
    def getPartNumber(self, obj):
        """获取物料名称"""      
        return obj.Part.FNumber if obj.Part else None
    def getPartModel(self, obj):
        """获取物料名称"""
        return obj.Part.FModel if obj.Part else None
    def getPartUnit(self, obj):
        """获取物料名称"""
        return obj.Part.FUnit.Name if obj.Part and obj.Part.FUnit else None
    def getQuantity(self, obj):
        """渲染为input"""
        value = to_decimal(obj.Quantity) if obj.Quantity else None
        return format_html(
            '<input  type="text" class="part-quantity-input" data-oid="{}" value="{}" style="width:120px;" />',
            obj.pk, value)
    def getDescription(self, obj):
        """渲染为input"""
        value = obj.Description
        return format_html(
            '<input  type="text" class="part-description-input" data-oid="{}" value="{}" style="width:120px;" />',
            obj.pk, value)
    def subAction(self, obj):
        result = format_html(
            f'<button type="button" id="part-change" class="el-button el-button--warning el-button--small" style="color: #ffffff;">变更保存</button>'
        )
        return result

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('add/', self.admin_site.admin_view(self.add_view), name='bmui_partsorder_add'),
            path('change/', self.admin_site.admin_view(self.change_part_view), name='bmui_partsorder_change'),
        ]
        return custom_urls + urls

    def get_list_display(self, request):
        # 例如：根据用户权限或请求参数动态返回不同的列
        OrderId = request.POST.get('POrder') or request.GET.get('POrder')
        if OrderId:
            return ['Idex', 'POrder', 'getPartNumber', 'getPartName','getPartModel','getPartUnit', 'getQuantity', 'Status', 'getDescription', 'subAction']

        else:
            return ['Idex', 'POrder', 'getPartNumber', 'getPartName','getPartModel','getPartUnit', 'Quantity', 'Status']

    def change_part_view(self, request):
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                oid = data.get("oid")
                quantity = data.get("quantity")
                description = data.get("description")
                obj = PartsOrder.objects.get(pk=oid)
                OrderId = data.get('POrder')
                if quantity in [None, '', 'None']:
                    obj.Quantity = 0
                else:
                    obj.Quantity = Decimal(str(quantity))
                if description is not None:
                    obj.Description = description
                obj.save()
                POrder.objects.filter(OrderId=OrderId).update(Status="已变更")
                return JsonResponse({"success": True, "message": "保存成功"})
            except Exception as e:
                return JsonResponse({"success": False, "message": str(e)}, status=500)
        return JsonResponse({"success": False, "message": "无效请求"}, status=400)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}        
        extra_context['partsHead'] = self.partsHead
        data = request.GET.get('POrder')
        extra_context['POrder'] = data if data else ''
        if request.method == "POST":
            return super().changelist_view(request, extra_context=extra_context)
        elif request.method == "GET":
            return super().changelist_view(request, extra_context=extra_context)

    def add_view(self, request, form_url = ..., extra_context =None):
        extra_context = extra_context or {}        
        extra_context['partsHead'] = self.partsHead
        extra_context['POrder'] = ''
        if request.method == "POST":
            try:
                result = {}
                parts = request.POST.getlist('Parts[]')
                descriptions = request.POST.getlist('Description[]')
                quantitys = request.POST.getlist('Quantity[]')
                OrderId = request.POST.get('POrder')
                extra_context['POrder'] = OrderId
                index = PartsOrder.objects.filter(POrder_id=OrderId).count() + 1
                for part, quantity, description in zip(parts, quantitys, descriptions):
                    if part.strip() and quantity.strip():
                        partObj = Material.objects.filter(FNumber=part).first()
                        if not partObj:
                            msg = (f"/r/n未找到物料: {part}, 请先添加物料")
                            self.message_user(request,  f"发生错误：{msg}", level="error")
                            return super().changelist_view(request, extra_context = extra_context)
                        PartsOrder.objects.update_or_create(POrder_id = OrderId, Part_id=partObj.FId, defaults={
                            'Status': "未就绪", 'Quantity': quantity, 'Description': description, 'Idex': index})
                        index += 1
                POrder.objects.filter(OrderId=OrderId).update(Status="已变更")
                self.message_user(request, " 零件追加成功！", level="success")
            except Exception as e:
                self.message_user(request, f"发生错误：{str(e)}", level="error")

            return super().changelist_view(request, extra_context = extra_context)

        return super().add_view(request, form_url, extra_context)

    getPartNumber.short_description = '物料编号'
    getPartModel.short_description = '物料型号'
    getPartUnit.short_description = '单位'
    getPartName.short_description = '物料名称'
    getQuantity.short_description = '数量'
    getDescription.short_description = '备注'
    subAction.short_description = '操作'
