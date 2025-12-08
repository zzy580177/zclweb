from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from .models import ProductionPlan, VProductionPlan, ProductionOrder, WorkOrder

@admin.register(ProductionPlan)
class ProductionPlanAdmin(admin.ModelAdmin):
    list_display = ['order_part', 'route', 'status', 'planned_quantity', 'planned_date']
    list_filter = ['status', 'planned_date']
    search_fields = ['order_part__order__order_id', 'route__bom_ver__material__number']
    change_list_template = "d_paichan/01_production_plan_change_list.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = '排产计划管理'
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
    list_display = ['order_number', 'plan', 'status', 'quantity', 'start_date', 'end_date']
    list_filter = ['status', 'start_date', 'end_date']
    search_fields = ['order_number', 'plan__order_part__order__order_id']

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = '生产订单管理'
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ['production_order', 'step', 'sequence', 'status', 'quantity', 'assigned_to', 'start_time']
    list_filter = ['status', 'assigned_to', 'start_time']
    search_fields = ['production_order__order_number', 'step__name']

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = '任务工单管理'
        return super().changelist_view(request, extra_context=extra_context)
