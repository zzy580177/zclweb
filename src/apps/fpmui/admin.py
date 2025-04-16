from django.contrib import admin
from django_starter.contrib.admin.tags import html_tags

from .models import *


@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = ['Id','Name','EqpType','Description',]

    

@admin.register(ProcessStep)
class ProcessStepAdmin(admin.ModelAdmin):
    list_display = ['StepId','Step','Route','Parameters','SeqNum','Description',]

    

@admin.register(ProcessRoute)
class ProcessRouteAdmin(admin.ModelAdmin):
    list_display = ['Id','Product_id','ApprovalStatus','Version','StartDay','Description',]

    

@admin.register(VirtualProcessRoute)
class VirtualProcessRouteAdmin(admin.ModelAdmin):
    list_display = ( 'Product_id', 'Version', 'steps_list_display', 'ApprovalStatus')
    search_fields = ('Version', 'Product_id')
    list_filter = ('Product_id',)
    ordering = ('Product_id', 'Version', )

    def steps_list_display(self, obj):
        """动态获取关联步骤列表并格式化显示"""
        steps = obj.get_steps_list()
        if steps:
            return ", ".join([f"步骤{step.SeqNum}: {step.Step.Name}" for step in steps])
        return "无关联步骤"

    steps_list_display.short_description = "相关工序列表"
    

