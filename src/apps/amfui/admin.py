from django.contrib import admin
from django_starter.contrib.admin.tags import html_tags
from django.db.models.functions import Concat, Cast, TruncDate,Trunc, Extract, Coalesce

from django.db.models import Sum, Q, FloatField

from .models import *

dayFilter = (('0', u'当天'),('1', u'本周'),('2', u'本月'), ('3', u'上个月'))
@admin.register(Alarmi)
class AlarmiAdmin(admin.ModelAdmin):
    list_display = ['AllarmID','AllarmString',]
    ordering = ['AllarmID']

    
@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ['Plant','Name','CellID','Type','Create','OnLineStr','WorkTMStr','Status',]
    ordering = ['Plant','Name','CellID','Type',]

    
class LiveStateFilter(admin.SimpleListFilter):
    title = '日期过滤'
    parameter_name = 'is_in_date'
    def lookups(self, request, model_admin):
        return dayFilter
    def queryset(self, request, queryset):
        # 当前日期格式
        cur_date = datetime.now().date()
        _start = cur_date
        _end = cur_date + timedelta(days=1)
        if self.value() == '1':
            _start = cur_date - timedelta(days=cur_date.weekday())
            _end = cur_date + timedelta(days=1)
        elif self.value() == '2':
            _start = cur_date.replace(day=1)
            _end = cur_date + timedelta(days=1)
        elif self.value() =='3':
            last_month = cur_date.replace(day=1) - timedelta(days=1)
            _start = last_month.replace(day=1)
            _end = last_month.replace(day=last_month.day) + timedelta(days=1)
        return queryset.filter(Check1__gte=_start, Check1__lt=_end).annotate(
            date=TruncDate('Check1')).values('date')

@admin.register(LiveStateManage)
class LiveStateManageAdmin(admin.ModelAdmin):
    list_filter = ['Cell_id', LiveStateFilter]
    change_list_template = 'amfui/livestate_change_list.html'
    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response
        metrics = {
           # 'onlineTm': Cast('OnLine',output_field=FloatField()),
            'tot_offline': Sum('TimeOff'),
            'tot_online':  Sum('OnLineTM'),    }
        response.context_data['headers'] = ['日期','设备编号','离线时长','在线时长',]
        response.context_data['summary'] = list(
            qs.annotate(OnLineTM=Cast('OnLine', FloatField()))
            .values( 'Check1__date','Cell_id',)
            .annotate(**metrics)
            .order_by('Check1__date','Cell_id')
        )
        for item in response.context_data['summary']:
            if item['tot_offline'] is not None:
                item['tot_offline'] = sec2TmStr(item['tot_offline'])
            if item['tot_online'] is not None:
                item['tot_online'] = sec2TmStr(item['tot_online'])
        return response

    

@admin.register(Pezzi)
class PezziAdmin(admin.ModelAdmin):
    list_display = ['Cell_id','WorkSheetID','Data','DataTime','Pezzi','ReqPezzi','ResidPezzi','PieceTime','EstimatedTm','TotWorkTm',]

    

@admin.register(Stato)
class StatoAdmin(admin.ModelAdmin):
    list_display = ['Cell_id','WorkSheetID','Data','DataTime','Stato','Alarm',]

    
class RecordFilter(admin.SimpleListFilter):
    title = '日期过滤'
    parameter_name = 'is_in_date'
    def lookups(self, request, model_admin):
        return dayFilter
    def queryset(self, request, queryset):
        # 当前日期格式
        cur_date = datetime.now().date()
        _start = cur_date
        _end = cur_date + timedelta(days=1)
        if self.value() == '1':
            _start = cur_date - timedelta(days=cur_date.weekday())
            _end = cur_date + timedelta(days=1)
        elif self.value() == '2':
            _start = cur_date.replace(day=1)
            _end = cur_date + timedelta(days=1)
        elif self.value() =='3':
            last_month = cur_date.replace(day=1) - timedelta(days=1)
            _start = last_month.replace(day=1)
            _end = last_month.replace(day=last_month.day) + timedelta(days=1)
        queryset = queryset.filter(StartTime__gte=_start, StartTime__lt=_end)
        return queryset#.values('Date','CellaID','Mode','WorkSheetID','Plant').order_by().annotate(
            #PowerOnSec_sum= Sum('PowerOnSec'),WorkingSec_sum = Sum('WorkingSec'),IdleTMSec_sum=Sum('IdleTMSec'))

@admin.register(RecordManage)
class RecordManageAdmin(admin.ModelAdmin):
    list_display = ['Cell_id','WorkSheetID','Date','StartTime','StopTime','Status','Mode','PowerOnTM','WorkingTM','FinishParts','IdleTMSec','PowerOnSec','WorkingSec',]
    list_filter = ['Cell_id', RecordFilter]

@admin.register(Record)
class RecordAdmin (admin.ModelAdmin):
    list_filter = ['Cell_id', RecordFilter]
    change_list_template = 'amfui/record_change_list.html'
    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response
        metrics = {
            'tot_adjustTM': Sum('PowerOnSec',filter=Q(Mode='调校模式')),
            'tot_poweron':  Sum('PowerOnSec'),
            'tot_workTM':   Sum('WorkingSec',filter=Q(Mode='普通模式')),
            'tot_idleTM':   Sum('IdleTMSec',filter=Q(Mode='普通模式')),
            'tot_parts':    Sum('FinishParts',filter=Q(Mode='普通模式')),
            }

        response.context_data['headers'] = ['日期','设备编号','工单编号','开机时长','调机时长','作业时长','待机时长','完成工件']
        response.context_data['summary'] = list(
            qs.filter().values( 'Date','Cell_id','WorkSheetID')
            .annotate(**metrics)
            .order_by()
        )
        for item in response.context_data['summary']:
            if item['tot_poweron'] is not None:
                item['tot_poweron'] = sec2TmStr(item['tot_poweron'])
            if item['tot_workTM'] is not None:
                item['tot_workTM'] = sec2TmStr(item['tot_workTM'])
            if item['tot_idleTM'] is not None:
                item['tot_idleTM'] = sec2TmStr(item['tot_idleTM'])
            if item['tot_adjustTM'] is not None:
                item['tot_adjustTM'] = sec2TmStr(item['tot_adjustTM'])
        return response
 

@admin.register(WorkSheet)
class WorkSheetAdmin(admin.ModelAdmin):
    list_display = ['Cell_id','Order_id','WorkSheetID','OrderID','Status','ProcessID','FinishParts','ReqParts','AddReqParts',]


    

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['OrderID','Status','Colour','ProductID','ReqParts',]

