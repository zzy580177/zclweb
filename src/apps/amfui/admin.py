from django.contrib import admin
from django_starter.contrib.admin.tags import html_tags

from .models import *
from django.db.models.functions import Concat, Cast, TruncDate,Trunc, Extract, Coalesce
from django.db.models import Min, Sum, Q, FloatField,F,Value, CharField

from import_export import resources
from django.http import HttpResponse
from openpyxl import Workbook

dayFilter = (('0', u'当天'),('1', u'本周'),('2', u'本月'), ('3', u'上个月'))
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
        return queryset.filter(Check1__gte=_start, Check1__lt=_end)

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
        return queryset.filter(StartTime__gte=_start, StartTime__lt=_end)



#@admin.register(Alarmi)
class AlarmiAdmin(admin.ModelAdmin):
    list_display = ['Id','AllarmString','TypeID','Description_Id',]
    ordering = ['Id']

    

@admin.register(LiveState)
class LiveStateAdmin(admin.ModelAdmin):
    list_filter = ['Cell_id', LiveStateFilter]
    change_list_template = 'amfui/livestate_change_list.html'
    def changelist_view(self, request, extra_context=None):
        try:
            response = super().changelist_view(request, extra_context)
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response
        metrics = {
            'tot_online':  Sum('OnLine'),    }
        response.context_data['headers'] = ['日期','车间','机台','机台编号','在线时长']
        response.context_data['summary'] = list(qs
            .values( 'Check1__date','Cell_id', 'Cell__Name', 'Cell__CellID', 'Cell__Plant')
            .annotate(**metrics)
            .order_by('-Check1__date','Cell__Plant', 'Cell__Name', 'Cell__CellID'))
        for item in response.context_data['summary']:
            if item['tot_online'] is not None:
                item['tot_online'] = sec2TmStr(item['tot_online'])
        return response
    def export_to_excel(self, request, queryset):
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=mymodel_export.xlsx'
        
        wb = Workbook()
        ws = wb.active
        ws.append(self.list_display)  # 表头
        for obj in queryset:
            ws.append([obj.Plant, obj.Name, obj.CellID, obj.Type, obj.Create, sec2TmStr(obj.OnLine), sec2TmStr(obj.WorkTM), obj.get_Alarmi_display()])
        wb.save(response)
        return response
    export_to_excel.short_description = "导出到Excel"
    actions = [export_to_excel]
    export_to_excel.choices = None


    

#class LiveStateManageAdmin(admin.ModelAdmin):
    list_display = ['id','Cell','Check1','Check2','WorkSheet','OnLine',]
    ordering = ['-Check1']
    

#@admin.register(Pezzi)
class PezziAdmin(admin.ModelAdmin):
    list_display = ['Cell__Plant','Cell__Name','Cell__CellID','WorkSheet_id','DataTime','Pezzi','ReqPezzi','ResidPezzi','PieceTime']
    
    ordering = ['-DataTime']
    

#@admin.register(Stato)
class StatoAdmin(admin.ModelAdmin):
    list_display = ['Cell__Plant','Cell__Name','Cell__CellID','WorkSheet_id','DataTime','Stato','Alarmi_id','TimeSpan',]
    ordering = ['-DataTime']
    

@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ['Plant','Name','CellID','Type','Create','OnLineStr','WorkTMStr','status']
    ordering = ['Plant','Name','CellID']
    def export_to_excel(self, request, queryset):
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=mymodel_export.xlsx'
        
        wb = Workbook()
        ws = wb.active
        ws.append(self.list_display)  # 表头
        for obj in queryset:
            ws.append([obj.Plant, obj.Name, obj.CellID, obj.Type, obj.Create, sec2TmStr(obj.OnLine), sec2TmStr(obj.WorkTM), obj.get_Alarmi_display()])
        wb.save(response)
        return response
    export_to_excel.short_description = "导出到Excel"
    actions = [export_to_excel]


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_filter = ['Cell_id', RecordFilter]
    change_list_template = 'amfui/record_change_list.html'
    def changelist_view(self, request, extra_context=None):
        try:
            response = super().changelist_view(request, extra_context)
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response
        metrics = {
            'tot_adjustTM': Sum('PowerOnSec',filter=Q(Mode='调校模式')),
            'tot_poweron':  Sum('PowerOnSec'),
            'tot_workTM':   Sum('WorkingSec',filter=Q(Mode='普通模式')),
            'tot_idleTM':   Sum('IdleTMSec',filter=Q(Mode='普通模式')),
            'min_estiTM':   Min('EstimatedSec',filter=Q(Mode='普通模式')),
            'tot_parts':    Sum('FinishParts',filter=Q(Mode='普通模式')),
            }

        response.context_data['headers'] = ['日期','车间','机台','机台编号','工单编号','开机时长','作业时长','待机时长','完成工件','预估剩余']
        response.context_data['summary'] = list(
            qs.filter().values( 'StartTime__date','Cell__Plant','Cell__Name','Cell__CellID','WorkSheet_id')
            .annotate(**metrics)
            .order_by('-StartTime__date','Cell__Plant','Cell__Name','Cell__CellID','WorkSheet_id')
        )
        for item in response.context_data['summary']:
            for key in ['tot_poweron','tot_workTM','tot_idleTM','tot_adjustTM','min_estiTM']:
                if item[key] is not None:
                    item[key] = sec2TmStr(item[key])
        return response
    def export_to_excel(self, request, queryset):
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=mymodel_export.xlsx'
        
        wb = Workbook()
        ws = wb.active
        ws.append(['Field1', 'Field2'])  # 表头
        for obj in queryset:
            ws.append([obj.field1, obj.field2])
        
        wb.save(response)
        return response
    export_to_excel.short_description = "导出到Excel"
    actions = [export_to_excel]
    

@admin.register(RecordManage)
class RecordManageAdmin(admin.ModelAdmin):
    #list_filter = ['Cell_id', RecordFilter]
    change_list_template = 'amfui/worksheet_change_list.html'
    def changelist_view(self, request, extra_context=None):
        try:
            response = super().changelist_view(request, extra_context)
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response
        metrics = {
            'tot_adjustTM': Sum('PowerOnSec',filter=Q(Mode='调校模式')),
            'tot_poweron':  Sum('PowerOnSec'),
            'tot_workTM':   Sum('WorkingSec',filter=Q(Mode='普通模式')),
            'tot_idleTM':   Sum('IdleTMSec',filter=Q(Mode='普通模式')),
            'min_estiTM':   Min('EstimatedSec',filter=Q(Mode='普通模式')),
            'tot_parts':    Sum('FinishParts',filter=Q(Mode='普通模式')),
            }

        response.context_data['headers'] = ['工单编号', '车间','机台','机台编号','开机时长','作业时长','待机时长','完成工件','预估剩余', '工单状态']
        response.context_data['summary'] = list(
            qs.filter().values( 'Cell__Plant','Cell__Name','Cell__CellID','WorkSheet_id', 'WorkSheet__Status')
            .annotate(**metrics)
            .order_by('WorkSheet__Status', 'Cell__Plant','Cell__Name','Cell__CellID','WorkSheet_id')
        )
        for item in response.context_data['summary']:
            for key in ['tot_poweron','tot_workTM','tot_idleTM','tot_adjustTM','min_estiTM']:
                if item[key] is not None:
                    item[key] = sec2TmStr(item[key])
        return response

    def export_to_excel(self, request, queryset):
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=mymodel_export.xlsx'
        
        wb = Workbook()
        ws = wb.active
        ws.append(['Field1', 'Field2'])  # 表头
        for obj in queryset:
            ws.append([obj.field1, obj.field2])
        
        wb.save(response)
        return response
    export_to_excel.short_description = "导出到Excel"
    actions = [export_to_excel]

#@admin.register(WorkSheet)
class WorkSheetAdmin(admin.ModelAdmin):
    list_display = ['Id','Cell__CellID','Order_id','Product_id','Status','ProcessID','FinishParts','ReqParts','AddReqParts',]

    

#@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['Id','Status','Colour','Product_id','ReqParts',]

    

