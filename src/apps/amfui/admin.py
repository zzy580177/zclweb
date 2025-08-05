from sys import path
from django.contrib import admin
from django.http import JsonResponse
import requests
from django_starter.contrib.admin.tags import html_tags
from django.db.models.functions import TruncDate
from .models import *
from django.test import Client
from django.urls import reverse, path
import json
from django.db.models import Sum, F, Q, Value, IntegerField, Prefetch
from django.db.models.functions import Coalesce, TruncDate, Concat
from django.db import transaction
import os
from django.core.paginator import Paginator

def format_seconds(seconds):
    if seconds is None:
        return "00:00"
    seconds = int(seconds)
    days = seconds // (24 * 3600)
    remaining_seconds = seconds % (24 * 3600)
    hours = remaining_seconds // 3600
    minutes = (remaining_seconds % 3600) // 60
    output = f"{minutes} 分"
    if days > 0:
        output = f"{days} 天 {hours} 时 "
    elif hours>0:
        output = f"{hours} 时 {minutes} 分"
    return output 

def format_api_data(item):
    """格式化API返回的原始数据"""
    return {
        "date_only": item["date_only"],
        "cell_str": item["cell_str"],
        "finish_sum": format_seconds(item["finish_sum"]),
        "idle_sum": format_seconds(item["idle_sum"]),
        "poweron_sum": format_seconds(item["poweron_sum"]),
        "working_sum": format_seconds(item["working_sum"]),
        "adjust_sum": format_seconds(item["adjust_sum"]),
        "estimated_sum": format_seconds(item["estimated_sum"]/100),
        "online_sum": format_seconds(item["online_sum"])
    }

#@admin.register(LiveState)
class LiveStateAdmin(admin.ModelAdmin):
    list_display = ['cell_name', 'date', 'online_sum', 'idle_sum', 'poweron_sum', 'working_sum']
    date_hierarchy = 'Check1'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request).exclude(Cell__Name="ZCL数采平台")
        
        # Annotate with aggregated values while preserving model instances
        return qs.annotate(
            date_only=TruncDate('Check1'),
            online_sum=Sum('OnLine'),
            idle_sum=Sum('WorkSheet__record__IdleTMSec'),
            poweron_sum=Sum('WorkSheet__record__PowerOnSec'),
            working_sum=Sum('WorkSheet__record__WorkingSec')
        ).order_by('-date_only')

    def cell_name(self, obj):
        return f"{obj.Cell.Name} {obj.Cell.CellID}"
    cell_name.short_description = '设备'
    cell_name.admin_order_field = 'Cell__Name'

    def date(self, obj):
        return obj.date_only
    date.short_description = '日期'
    date.admin_order_field = 'date_only'

    def online_sum(self, obj):
        return obj.online_sum #format_seconds(obj.online_sum)
    online_sum.short_description = '在线时长(总和)'

    def idle_sum(self, obj):
        return obj.idle_sum #format_seconds(obj.idle_sum)
    idle_sum.short_description = '空闲时间(总和)'
    
    def poweron_sum(self, obj):
        return obj.poweron_sum #format_seconds(obj.poweron_sum)
    poweron_sum.short_description = '开机时间(总和)'
    
    def working_sum(self, obj):
        return format_seconds(obj.working_sum)
    working_sum.short_description = '工作时间(总和)'

@admin.register(Stato)
class StatoAdmin(admin.ModelAdmin):
    list_display = ['name_id','date','start_time','stop_time','alarm_id','alarmi_str',]

    def name_id(self, obj):
        return f"{obj.Cell}"
    name_id.short_description = '设备 ID'

    def date(self, obj):
        return obj.DataTime.date() if obj.DataTime else None
    date.short_description = '日期'
    date.admin_order_field = 'DataTime'

    def start_time(self, obj):
        return obj.DataTime.time() if obj.DataTime else None
    start_time.short_description = '开始时间'
    
    def stop_time(self, obj):
        stoptm = obj.DataTime + timedelta(seconds=obj.TimeSpan) if obj.DataTime else None
        return stoptm.time() if stoptm else None
    stop_time.short_description = '结束时间'

    def alarm_id(self, obj):
        return obj.Alarmi__AlarmID if obj.Alarmi else None
    alarm_id.short_description = '报警ID'
    alarm_id.admin_order_field = 'Alarmi__AlarmID'

    def alarmi_str(self, obj):
        return obj.Alarmi__AlarmString if obj.Alarmi else None
    alarmi_str.short_description = '报警信息'
    alarmi_str.admin_order_field = 'Alarmi__AlarmString'

    def get_queryset(self, request):
        return super().get_queryset(request).exclude(Cell__Name="ZCL数采平台").filter(
            Q(Stato=2))

@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = [
        'Plant', 'name_id', 'Type', 'cell_stato', 'IP', 
        'formatted_create', 'formatted_on_line', 'formatted_work_tm'
    ]
    def name_id(self, obj):
        return f"{obj.Name} {obj.CellID}"
    name_id.short_description = '设备名称 ID'

    def formatted_create(self, obj):
        return obj.Create.date() if obj.Create else None
    formatted_create.short_description = '创建日期'
    formatted_create.admin_order_field = 'Create'

    def formatted_on_line(self, obj):
        return format_seconds(obj.OnLine)
    formatted_on_line.short_description = '在线时长'
    formatted_on_line.admin_order_field = 'OnLine'

    def formatted_work_tm(self, obj):
        return format_seconds(obj.WorkTM)
    formatted_work_tm.short_description = '作业时长'
    formatted_work_tm.admin_order_field = 'WorkTM'

    def cell_stato(self, obj):
        if obj.Name == "ZCL数采平台":
            isoffLine=(datetime.now() - obj.latest_live_state[0].Check1) > timedelta(minutes=5)
            return "离线" if isoffLine else "在线"
        return obj.get_Stato_display()
    cell_stato.short_description = '当前状态'
    cell_stato.admin_order_field = 'Stato'

    def get_queryset(self, request):
        qs = super().get_queryset(request).prefetch_related(
            Prefetch(
                'livestate_set', 
                queryset=LiveState.objects.order_by('-Check1')[:1],
                to_attr='latest_live_state'))
        return qs

@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    change_list_template = 'amfui/record_changelist.html'

    list_per_page = 20

    def changelist_view(self, request, extra_context=None):
        api_url = "http://127.0.0.1:8001/api/amfui/record/aggregated"
        params = {
            'page': request.GET.get('p', 1),
            'size': self.list_per_page
        }
        response = requests.get(api_url, params=params)
        
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', [])
            paginator = Paginator(data, self.list_per_page)
            page = paginator.get_page(params['page'])
        else:
            page = Paginator([], self.list_per_page).get_page(1)

        extra_context = extra_context or {}
        extra_context.update({
            'api_data': [format_api_data(item) for item in page],
            'paginator': page.paginator,
            'page_obj': page
        })
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(WorkSheet)
class WorkSheetAdmin(admin.ModelAdmin):
    list_display = [
        'Id', 'Order', 'Product_id', 'ProcessID',
        'req_parts', 'FinishParts', 'Status',
        'poweron_sum', 'working_sum', 'idle_sum',
        'estimated_sum']
    list_filter = ['Id', 'Order','Status']

    def req_parts(self, obj):
        return (obj.ReqParts or 0) + (obj.AddReqParts or 0)
    req_parts.short_description = '需求工件数'

    def get_queryset(self, request):
        qs = super().get_queryset(request).exclude(Id="未绑定工单")
        return qs.annotate(
            total_idle=Coalesce(Sum('record_set__IdleTMSec',output_field=IntegerField()), 0),
            total_power=Coalesce(Sum('record_set__PowerOnSec',output_field=IntegerField()), 0),
            total_work=Coalesce(Sum('record_set__WorkingSec',output_field=IntegerField()), 0),
            total_estimate=Coalesce(Sum('record_set__EstimatedSec',output_field=IntegerField()), 0)
        )

    def save_related(self, request, form, formsets, change):
        stats = form.instance.record_set.aggregate(
            finish=Sum('FinishParts'),
            idle=Sum('IdleTMSec'),
            power=Sum('PowerOnSec'),
            work=Sum('WorkingSec'),
            estimate=Sum('EstimatedSec')
        )

    def idle_sum(self, obj):
        return format_seconds(getattr(obj, 'total_idle', 0))
    idle_sum.short_description = '空闲时间'
    idle_sum.admin_order_field = 'total_idle'

    def poweron_sum(self, obj):
        return format_seconds(getattr(obj, 'total_power', 0))
    poweron_sum.short_description = '开机时间'
    poweron_sum.admin_order_field = 'total_power'

    def working_sum(self, obj):
        return format_seconds(getattr(obj, 'total_work', 0))
    working_sum.short_description = '工作时间'
    working_sum.admin_order_field = 'total_work'

    def estimated_sum(self, obj):
        return format_seconds(getattr(obj, 'total_estimate', 0)/100)
    estimated_sum.short_description = '预估时间'
    estimated_sum.admin_order_field = 'total_estimate'
