from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from .models import ProductionPlan, VProductionPlan, ProductionOrder, WorkOrder
from apps.a_wuliao.models import Attribute

@admin.register(ProductionPlan)
class ProductionPlanAdmin(admin.ModelAdmin):
    list_display = ['order_part', 'route', 'cnc_route', 'status', ]
    list_filter = ['status', 'order_part__order__deadline']
    #search_fields = ['order_part__order__order_id', 'route__bom_ver__material__number']
    change_list_template = "d_paichan/01_production_plan_change_list.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = '排产计划管理'    
        eqp_qs = Attribute.objects.filter(description__icontains="设备").values('name', 'attribute_id', 'description').distinct()
        parm_qs = Attribute.objects.filter(description__icontains="工艺参数").values('name', 'attribute_id', 'description', 'key').distinct()
        
        # 初始化STEPARAM字典
        if 'STEPARAM' not in extra_context:
            extra_context['STEPARAM'] = {'EQP': {}, 'Params': {}}
        
        # 修复语法错误：使用if而不是with
        extra_context['STEPARAM']['EQP']['UNCNC'] = [{'label': data['name'], 'value': data['attribute_id']} for data in eqp_qs if data.get('description') == '设备']
        extra_context['STEPARAM']['EQP']['CNC'] = [{'label': data['name'], 'value': data['attribute_id']} for data in eqp_qs if data.get('description') == 'CNC设备']
        extra_context['STEPARAM']['Params']['UNCNC'] = [{'label': data['name'], 'key': data['key']} for data in parm_qs if data.get('description') == '工艺参数']
        extra_context['STEPARAM']['Params']['CNC'] = [{'label': data['name'], 'key':  data['key']} for data in parm_qs if data.get('description') == 'CNC工艺参数']

        return super().changelist_view(request, extra_context=extra_context)

@admin.register(VProductionPlan)
class VProductionPlanAdmin(admin.ModelAdmin):
    list_display = ['order_part', 'route', 'status', 'planned_quantity', 'planned_date']
    list_filter = ['status', 'planned_date']
    search_fields = ['order_part__order__order_id']

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = '虚拟排产计划管理'
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
    list_display = ['order', ]
    list_filter = ['status', ]
    search_fields = ['order',]

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = '生产订单管理'
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ['plan', 'process', 'sequence', 'status', 'quantity', 'assigned_to', 'start_time']
    list_filter = ['status', 'assigned_to', 'start_time']
    search_fields = ['plan__order_number', ]

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = '任务工单管理'
        return super().changelist_view(request, extra_context=extra_context)
