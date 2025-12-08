from django.contrib import admin
from django_starter.contrib.admin.tags import html_tags, elementui_tags
from django.contrib.admin import SimpleListFilter
from django.db.models import Q

from .models import *


def delete_selected(modeladmin, request, queryset):
    count = queryset.count()
    queryset.delete()
    modeladmin.message_user(request, f"成功删除了 {count} 条记录！", level="success")
delete_selected.short_description = "删除选中项"

class GroupFilter(SimpleListFilter):
    title = '一级分类'
    parameter_name = 'group'

    def lookups(self, request, model_admin):
        return [(choice[0], f"{choice[0]} - {choice[1]}") for choice in MaterialGroup.GROUP_CHOICES]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(group=self.value())
        return queryset
class SubGroupFilter(SimpleListFilter):
    title = '二级分类'
    parameter_name = 'sub_group'

    def lookups(self, request, model_admin):
        group_value = request.GET.get('group')
        if group_value:
            return [(choice[0], f"{choice[0]} - {choice[1]}") for choice in MaterialGroup.SUB_GROUP_CHOICES 
                    if choice[0].startswith(group_value)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(sub_group=self.value())
        return queryset
class MinGroupFilter(SimpleListFilter):
    title = '三级分类'
    parameter_name = 'min_group'

    def lookups(self, request, model_admin):
        sub_group_value = request.GET.get('sub_group')
        if sub_group_value:
            existing_min_groups = MaterialGroup.objects.filter(
                sub_group=sub_group_value, min_group__isnull=False
            ).exclude(min_group='').values_list('min_group', flat=True).distinct()
            return [(mg, f"三级分类 - {mg}") for mg in existing_min_groups]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(min_group=self.value())
        return queryset

class MGroupFilter(SimpleListFilter):
    title = '一级分类'
    parameter_name = 'group__group'

    def lookups(self, request, model_admin):
        return [(choice[0], f"{choice[0]} - {choice[1]}") for choice in MaterialGroup.GROUP_CHOICES]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(group__number__startswith=self.value())
        return queryset
class SubMGroupFilter(SimpleListFilter):
    title = '二级分类'
    parameter_name = 'group__sub_group'

    def lookups(self, request, model_admin):
        group_value = request.GET.get('group__group')
        if group_value:
            return [(choice[0], f"{choice[0]} - {choice[1]}") for choice in MaterialGroup.SUB_GROUP_CHOICES 
                    if choice[0].startswith(group_value)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(group__number__startswith=self.value())
        return queryset
class MinMGroupFilter(SimpleListFilter):
    title = '三级分类'
    parameter_name = 'group__min_group'

    def lookups(self, request, model_admin):
        sub_group_value = request.GET.get('group__sub_group')
        if sub_group_value:
            existing_min_groups = MaterialGroup.objects.filter(
                sub_group=sub_group_value, min_group=''
            ).values('name', 'number').distinct()
            return [(m['number'], f"{m['number']} - {m['name']}") for m in existing_min_groups]
        return []
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(group__number__startswith=self.value())
        return queryset

class BGroupFilter(SimpleListFilter):
    title = '一级分类'
    parameter_name = 'material__group__group'

    def lookups(self, request, model_admin):
        return [(choice[0], f"{choice[0]} - {choice[1]}") for choice in MaterialGroup.GROUP_CHOICES]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(material__group__number__startswith=self.value())
        return queryset
class SubBGroupFilter(SimpleListFilter):
    title = '二级分类'
    parameter_name = 'material__group__sub_group'

    def lookups(self, request, model_admin):
        group_value = request.GET.get('material__group__group')
        if group_value:
            return [(choice[0], f"{choice[0]} - {choice[1]}") for choice in MaterialGroup.SUB_GROUP_CHOICES 
                    if choice[0].startswith(group_value)]
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(material__group__number__startswith=self.value())
        return queryset
class MinBGroupFilter(SimpleListFilter):
    title = '三级分类'
    parameter_name = 'material__group__min_group'

    def lookups(self, request, model_admin):
        sub_group_value = request.GET.get('material__group__sub_group')
        if sub_group_value:
            existing_min_groups = MaterialGroup.objects.filter(
                sub_group=sub_group_value, min_group=''
            ).values('name', 'number').distinct()
            return [(m['number'], f"{m['number']} - {m['name']}") for m in existing_min_groups]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(material__group__number__startswith=self.value())
        return queryset

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ['attribute_id','description_option','name_option', 'key_option', 'sub_actions']
    list_filter = ['description']
    change_list_template = "a_wuliao/00_attribute_change_list.html"
    actions = [delete_selected]
    ordering = ['description', 'attribute_id']

    def description_option(self, obj):
        return html_tags.input_tag(obj.description)
    description_option.short_description = '属性'
    def name_option(self, obj):
        return html_tags.input_tag(obj.name)
    name_option.short_description = '名称'
    def key_option(self, obj):
        return html_tags.input_tag(obj.key)
    key_option.short_description = '备注'
    def sub_actions(self, obj):
        return elementui_tags.el_button('primary','变更')
    sub_actions.short_description = '操作'

@admin.register(MaterialGroup)
class MaterialGroupAdmin(admin.ModelAdmin):
    list_display = ['group_id','name','parent','number','group','sub_group','min_group',]
    list_display_links = ['group_id','name','number','group','sub_group','min_group',]
    list_filter = [GroupFilter, SubGroupFilter, MinGroupFilter]  
    change_list_template = "a_wuliao/01_group_change_list.html"
    actions = [delete_selected]  
    ordering = ['level', 'group', 'sub_group', 'min_group','number']

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['material_id','group','number','name','helpcode','model','unit','source','description',]
    list_display_links = ['material_id','number','name','helpcode','model','source','description',]
    list_filter = [MGroupFilter, SubMGroupFilter, MinMGroupFilter]  
    change_list_template = "a_wuliao/02_material_change_list.html"
    ordering = ['group','number']
  
@admin.register(BomVersion)
class BomVersionAdmin(admin.ModelAdmin):
    list_display = ['material_name','material_number','version','base','change_reason','status','creator',]
    list_display_links = ['version','change_reason','status','creator',]
    ordering = ['material']
    list_filter = [BGroupFilter, SubBGroupFilter, MinBGroupFilter]   
    change_list_template = "a_wuliao/03_version_change_list.html"
    def material_name(self, obj):
        return obj.material.name
    def material_number(self, obj):
        return obj.material.number
    material_number.short_description = '物料号'  
    material_name.short_description = '物料名'      

    

@admin.register(Bom)
class BomAdmin(admin.ModelAdmin):
    list_display = ['version','p_material','c_material','quantity','level','remark',]
    change_list_template = "a_wuliao/04_bom_change_list.html"

