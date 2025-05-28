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
from .models import *

def delete_selected(modeladmin, request, queryset):
    """自定义动作：删除选中项"""
    count = queryset.count()
    queryset.delete()
    modeladmin.message_user(request, f"成功删除了 {count} 条数据！", level="success")
delete_selected.short_description = "删除选中项"

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
           # path('addlist/', self.admin_site.admin_view(self.addlist_view), name='bmui_material_addlist'),
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

@admin.register(POrder)
class POrderAdmin(admin.ModelAdmin):
    list_display = ['CreateTime','OrderId', 'Product_id', 'LotId', 'DeadLine', 'Status',  'Owner', 'WH', 'Audit', 'Description']
    change_list_template = "pmcui/porder_change_list.html"
    actions = ['delete_selected']

    tableHead = ['订单号','产品型号','产品批次号', '交货日期','订单状态','制单员', '仓管', '审核','备注']
    partsHead = ['物料编号','物料名称', '物料型号','单位','数量','备注']
    tabletype = [
            {'type':'text','name':'OrderId[]','required': 'required'},{'type':'text','name':'Product_id[]','required': 'required'},
            {'type':'text','name':'LotId[]','required': ''},{'type':'date','name':'DeadLine[]','required': 'required'},
            {'type':'select','name':'Status[]','required': '', 'options': ['新建', '已变更', '已审核', '已完成', '已取消']}, 
            {'type':'text','name':'Owner[]', 'required': ''}, {'type':'text','name':'WH[]','required': ''}, 
            {'type':'text','name':'Audit[]', 'required': ''}, {'type':'text','name':'FDescription[]','required': ''}]
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}        
        extra_context['partsHead'] = self.partsHead  
        extra_context['tableHead'] = self.tableHead        
        extra_context['tabletype'] = self.tabletype
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
            path('add/', self.admin_site.admin_view(self.add_view), name='bmui_porder_add'),
            path('getgroup/', self.admin_site.admin_view(self.getgroup_view), name='bmui_porder_getgroup'),
            path('addlist/', self.admin_site.admin_view(self.addlist_view), name='bmui_porder_addlist'),
        ]
        return custom_urls + urls


    def add_view(self, request, form_url='', extra_context=None):
        if request.method == "POST":
            try:
                result = {}
                for each in self.tabletype:
                    key = each['name'] 
                    result[key] = request.POST.getlist(each['name'])  

                for OrderId, Product_id, LotId, DeadLine, Status,  Owner, WH, Audit, FDescription in zip(
                    result['OrderId[]'], result['Product_id[]'], result['LotId[]'], result['DeadLine[]'], result['Status[]'],
                    result['Owner[]'], result['WH[]'], result['Audit[]'], result['FDescription[]']):
                    if OrderId.strip():
                        POrder.objects.update_or_create(OrderId=OrderId, defaults={ 'Product_id':Product_id, 
                            'LotId': LotId,'DeadLine': DeadLine,'Status': Status, 'Owner': Owner,
                            'WH': WH, 'Description': FDescription, 'Audit': Audit})
                self.message_user(request, " 新订单创建成功！", level="success")
            except Exception as e:
                self.message_user(request, f"发生错误：{str(e)}", level="error")
            return self.changelist_view(request)

        return super().add_view(request, form_url, extra_context)

    def addlist_view(self, request, form_url='', extra_context=None):
        msg = ''
        if request.method == "POST":
            try:
                payload = json.loads(request.body)
                parts = payload.get("parts", [])
                order = payload.get("order", None)  # 获取 POrderId
                if not parts:
                    return JsonResponse({"success": False, "message": "material 数据为空"}, status=400)
                if order:
                    POrder.objects.update_or_create(OrderId=order['POrder'], Product_id=order['Product'], 
                        defaults={'LotId': order['LotId'],'DeadLine': order['DeadLine'],'Status': "新建", 'Owner': order['Owner']})

                with transaction.atomic():
                    FNumbers, FNames, FModels, FUnits, Quantitys, Descriptions = zip(*parts)
                    if not FNumbers and not FNames:
                        self.message_user(request, "提交的数据不完整，请检查后重试！", level="error")
                        return self.changelist_view(request)
                    index = 1
                    for FNumber, FName, FModel, FUnit, Quantity, Description in zip(FNumbers, FNames, FModels, FUnits, Quantitys, Descriptions):
                        if FNumber.strip() and FUnit.strip():
                            partObj = Material.objects.filter(FNumber=FNumber, FName=FName,FModel=FModel).first()
                            PartsOrder.objects.update_or_create(POrder_id = order['POrder'], Part_id=partObj.FId, defaults={
                                'Status': "未就绪", 'Quantity': Quantity, 'Description': Description, 'Idex': index})
                            index += 1
                        elif FName.strip() and FModel.strip():
                            partObj = Material.objects.filter(FModel=FModel).first()
                            if not partObj:
                                msg = msg + (f"/r/n未找到物料: {FModel} {FName}, 请先添加物料")
                                continue
                            PartsOrder.objects.update_or_create(POrder_id = order['POrder'], Part_id=partObj.FId, defaults={
                                'Status': "未就绪", 'Quantity': Quantity, 'Description': Description, 'Idex': index})
                            index += 1
                    return JsonResponse({"success": True, "message": "BOM 数据保存成功" + msg})

            except Exception as e:
                return JsonResponse({"success": False, "message": str(e)}, status=500)

    def getgroup_view(self, request):
        fclass = request.GET.get('FClass')
        if not fclass:
            return JsonResponse([], safe=False)

        group_codes = POrder.objects.filter(
            FGroupCode=fclass, FSubGroupCode='' 
        ).values_list('FNumber', 'FName').distinct()
        return JsonResponse(list(group_codes), safe=False)    


@admin.register(PartsOrder)
class PartsOrderAdmin(admin.ModelAdmin):
    list_display = ['POrder', 'Idex','getPartNumber', 'getPartName','getPartModel','getPartUnit', 'Quantity', 'Status', 'DeadLine', 'Cost']
    list_filter = ['POrder']
    actions = ['delete_selected']
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

    getPartNumber.short_description = '物料编号'
    getPartModel.short_description = '物料型号'
    getPartUnit.short_description = '单位'
    getPartName.short_description = '物料名称'
