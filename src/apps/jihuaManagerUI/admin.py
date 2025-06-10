from django.contrib import admin
from django_starter.contrib.admin.tags import html_tags
from django.http import JsonResponse
from django.urls import path
import json
from django.db import transaction
from django.utils.html import format_html

from .models import *
from apps.bmui.models import Material
from apps.pmcui.models import PartsOrder

statusOptions = ['新建', '已就绪', '已变更', '已审核', '已完成', '已取消']

@admin.register(POrder)
class POrderAdmin(admin.ModelAdmin):
    list_display = ['OrderId', 'Product_id', 'LotId', 'DeadLine', 'status_option', 'subAction']
    list_filter = ['Status', ('CreateTime', admin.DateFieldListFilter)]
    change_list_template = "pmcui/porder_change_list.html"

    tableHead = ['订单号','产品型号','产品批次号', '交货日期','订单状态','制单员', '仓管', '审核','备注']
    partsHead = ['物料编号','物料名称', '物料型号','单位','数量','备注']
    statusOptions = statusOptions
    tabletype = [
            {'type':'text','name':'OrderId[]','required': 'required'},{'type':'text','name':'Product_id[]','required': 'required'},
            {'type':'text','name':'LotId[]','required': ''},{'type':'date','name':'DeadLine[]','required': 'required'},
            {'type':'select','name':'Status[]','required': '', 'options': statusOptions}, 
            {'type':'text','name':'Owner[]', 'required': ''}, {'type':'text','name':'WH[]','required': ''}, 
            {'type':'text','name':'Audit[]', 'required': ''}, {'type':'text','name':'FDescription[]','required': ''}]

    def status_option(self, obj):
        options = ''.join(
            f'<option value="{status}" {"selected" if obj.Status == status else ""}>{status}</option>'
            for status in self.statusOptions
        )
        return format_html(
            f'<select id="status_option_{obj.pk}" class="status-select" data-oid="{obj.pk}">{options}</select>'
        )
    status_option.short_description = '订单状态'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}        
        extra_context['partsHead'] = self.partsHead  
        extra_context['tableHead'] = self.tableHead        
        extra_context['tabletype'] = self.tabletype
        extra_context['status_options'] = self.statusOptions
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
            path('addlist/', self.admin_site.admin_view(self.addlist_view), name='bmui_porder_addlist'),
            path('change_status/',self.admin_site.admin_view(self.change_status_view), name='bmui_porder_change_status'
            ),
        ]
        return custom_urls + urls

    def subAction(self, obj):
        result = format_html(
            f'<button type="button" id="status-change" class="el-button el-button--warning el-button--small" style="color: #ffffff;">变更保存</button>'
            f'<a href="/amf/pmcui/partsorder/?POrder__OrderId__exact={obj.pk}&POrder={obj.pk}" '
            'class="el-button el-button--info el-button--small">子项变更</a>'
        )
        return result
    subAction.short_description = '操作'

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
                                msg = (f"/r/n未找到物料: {FModel} {FName}, 请先添加物料")
                                return JsonResponse({"success": False, "message": msg}, status=500)
                            PartsOrder.objects.update_or_create(POrder_id = order['POrder'], Part_id=partObj.FId, defaults={
                                'Status': "未就绪", 'Quantity': Quantity, 'Description': Description, 'Idex': index})
                            index += 1
                    return JsonResponse({"success": True, "message": "BOM 数据保存成功" + msg})

            except Exception as e:
                return JsonResponse({"success": False, "message": str(e)}, status=500)

    def change_status_view(self, request):
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                object_id = data.get("oid") or data.get("object_id")
                status = data.get("status")
                POrder.objects.filter(pk=object_id).update(Status=status)
                return JsonResponse({"success": True, "message": "保存成功"})
            except Exception as e:
                return JsonResponse({"success": False, "message": str(e)}, status=500)
        return JsonResponse({"success": False, "message": "无效请求"}, status=400)

@admin.register(OutBoundManag)
class OutBoundManagAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                "fields": ["url", "title", "content", "sites"],
            },
        ),
        (
            "Advanced options",
            {
                "classes": ["collapse"],
                "fields": ["registration_required", "template_name"],
            },
        ),
    ]

    

