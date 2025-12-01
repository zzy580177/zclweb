from django.contrib import admin
from django_starter.contrib.admin.tags import html_tags, elementui_tags

from .models import *
from apps.a_wuliao.models import BomVersion

def delete_selected(modeladmin, request, queryset):
    count = queryset.count()
    queryset.delete()
    modeladmin.message_user(request, f"成功删除了 {count} 条记录！", level="success")
delete_selected.short_description = "删除选中项"
statusOptions = ['新建', '已就绪', '已变更', '已审核', '已完成', '已取消']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id','product_id','lot_id', 'deadline_option','delivery_day_option','description_option','status_option','sub_actions']
    list_filter = ['status']
    actions = [delete_selected]  
    change_list_template = "b_jihua/00_order_change_list.html"
    def delivery_day_option(self, obj):
        return html_tags.input_tag(obj.delivery_day, 'date')
    delivery_day_option.short_description = '交货日期'

    def deadline_option(self, obj):
        return html_tags.input_tag(obj.deadline, 'date')
    deadline_option.short_description = '计划交付日期'

    def description_option(self, obj):
        return html_tags.input_tag(obj.description)
    description_option.short_description = '备注'

    def status_option(self, obj):
        return html_tags.select_tag(obj.status, statusOptions)
    status_option.short_description = '订单状态'

    def sub_actions(self, obj):
        return elementui_tags.el_button('primary','变更')
    sub_actions.short_description = '操作'
    
    def changelist_view(self, request, extra_context = None):
        if extra_context is None:
            extra_context = {}
        extra_context['orders_options'] = self._getOrderList()
        return super().changelist_view(request, extra_context)
    
    def _getOrderList(self):
        orders = Order.objects.all().values('order_id')
        order_list = [order['order_id'] for order in orders]
        return order_list

@admin.register(OrderParts)
class OrderPartsAdmin(admin.ModelAdmin):
    list_display = ['id', 'order','material_number','material_name','version_option','deadline_option','quantity_option','status',
                    'description_option', 'sub_actions']
    list_filter = ['order','material','status',]
    ordering = ['-id']
    actions = [delete_selected]
    change_list_template = "b_jihua/01_orderparts_change_list.html"

    def material_number(self, obj):
        return obj.material.number
    material_number.short_description = '物料编号'

    def material_name(self, obj):
        return obj.material.name
    material_name.short_description = '物料名称'

    def version_option(self, obj):
        history_versions = list(BomVersion.objects.filter(
            material=obj.material).values_list('version', flat=True).order_by('-create_time'))
        return html_tags.select_tag(obj.version ,history_versions)
    version_option.short_description = '物料版本'

    def deadline_option(self, obj):
        return html_tags.input_tag(obj.deadline, 'date')
    deadline_option.short_description = '计划交付日期'

    def quantity_option(self, obj):
        return html_tags.input_tag(obj.quantity, 'number')
    quantity_option.short_description = '数量'

    def description_option(self, obj):
        return html_tags.input_tag(obj.description)
    description_option.short_description = '备注'



    def sub_actions(self, obj):
        return elementui_tags.el_button('primary','变更')
    sub_actions.short_description = '操作'
    def changelist_view(self, request, extra_context = None):
        if extra_context is None:
            extra_context = {}
        extra_context['orders_options'] = self._getOrderList()
        return super().changelist_view(request, extra_context)
    
    def _getOrderList(self):
        orders = Order.objects.all().values('order_id')
        order_list = [order['order_id'] for order in orders]
        return order_list
