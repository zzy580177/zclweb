from django.contrib import admin
from django_starter.contrib.admin.tags import html_tags

from .models import *


def delete_selected(modeladmin, request, queryset):
    count = queryset.count()
    queryset.delete()
    modeladmin.message_user(request, f"成功删除了 {count} 条记录！", level="success")
delete_selected.short_description = "删除选中项"
statusOptions = ['新建', '已就绪', '已变更', '已审核', '已完成', '已取消']




@admin.register(MaterialParm)
class MaterialParmAdmin(admin.ModelAdmin):
    list_display = ['id','bom_ver','size','stuff','cost','surface','description',]
    list_display_links = ['id','size','stuff','cost','surface','description',]
    actions = [delete_selected]  
    change_list_template = "c_gongyi/00_materialParm_change_list.html"


    

@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = ['id','create_time','update_time','deleted_at','deleted_by','name','type','ucost','hcost','description',]
    list_display_links = ['id','create_time','update_time','deleted_at','deleted_by','name','ucost','hcost','description',]
    list_filter = ['type']
    actions = [delete_selected]  
    change_list_template = "c_gongyi/01_step_change_list.html"
    
    def changelist_view(self, request, extra_context = None):
        if extra_context is None:
            extra_context = {}
        extra_context['eqpType'] = self._getStepTypeList()
        return super().changelist_view(request, extra_context)
    
    def _getStepTypeList(self):
        typeList = []
        types = Attribute.objects.filter(description='工序分类')
        for t in types:
            typeList.append(t.name)
        return typeList

@admin.register(Craft)
class CraftAdmin(admin.ModelAdmin):
    change_list_template = "c_gongyi/02_craft_change_list.html"
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}        
        qs = Attribute.objects.filter(description="工序分类").values('name', 'attribute_id').distinct()
        extra_context['StepGroup'] = [{'label':data['name'], 'value' :data['attribute_id']} for data in qs]
        return super().changelist_view(request, extra_context=extra_context)
 
@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ['id','route','subroute','seqnum','params','description',]
    list_display_links = ['id','seqnum','params','description',]
   

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['id','create_time','update_time','deleted_at','deleted_by','bom_ver','is_cnc','product_id','approval_status','params','description',]
    list_display_links = ['id','create_time','update_time','deleted_at','deleted_by','is_cnc','product_id','approval_status','params','description',]


    

@admin.register(VirtualProcessRoute)
class VirtualProcessRouteAdmin(admin.ModelAdmin):
    list_display = ['id','create_time','update_time','deleted_at','deleted_by','bom_ver','is_cnc','product_id','approval_status','params','description',]
    list_display_links = ['id','create_time','update_time','deleted_at','deleted_by','is_cnc','product_id','approval_status','params','description',]

@admin.register(CNCProcess)
class CNCProcessAdmin(admin.ModelAdmin):
    list_display = ['id','create_time','update_time','deleted_at','deleted_by','route','seqnum','params','description',]

    

@admin.register(CNCProgram)
class CNCProgramAdmin(admin.ModelAdmin):
    list_display = ['id','create_time','update_time','deleted_at','deleted_by','cnc_process','program_name','equipment_model','fixture_name','simulation_time','path','description',]


    

@admin.register(CNCCraft)
class CNCCraftAdmin(admin.ModelAdmin):
    list_display = ['id','process','step_num','step','params',]

