from django.contrib import admin

from .models import *
from django.db.models import Min, Sum, Q,F,Value

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

def export_as_xml(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=mymodel_export.xlsx'
    if modeladmin.__class__.__name__ != 'CellAdmin':
        queryset = modeladmin.queryset
    wb = Workbook()
    ws = wb.active
    ws.append(['ID'] + modeladmin.list_displayHead)
    modeladmin.appendXmlWs(ws, queryset);
    wb.save(response)
    return response
export_as_xml.short_description = "导出到Excel"

def changelist_view(modeladmin, request, extra_context=None):
    try:
        if request.method=="POST":
            response = super(modeladmin.__class__, modeladmin).changelist_view(request, extra_context)

        elif request.method=="GET":
            response = super(modeladmin.__class__, modeladmin).changelist_view(request, extra_context)
            qs= modeladmin.get_select_queryset(request, response.context_data['cl'].queryset)
            response.context_data['headers'] = modeladmin.list_displayHead
            response.context_data['summary'] = qs
            modeladmin.queryset = qs
    except (AttributeError, KeyError) as error:
        print(f"An error occurred: {error}")
        return response
    return response

@admin.register(LiveState)
class LiveStateAdmin(admin.ModelAdmin):
    list_filter = ['Cell_id', LiveStateFilter]
    actions = [export_as_xml]
    change_list_template = 'amfui/livestate_change_list.html'
    list_displayHead = ['日期','车间','机台','机台编号','在线时长']
    def appendXmlWs(self, ws, queryset):
        i = 0
        for obj in queryset:
            i = i + 1
            ws.append([i, obj['Check1__date'], obj['Cell__Plant'], obj['Cell__Name'], obj['Cell__CellID'], obj['tot_online']])

    def get_select_queryset(self, request, queryset):
        metrics = {'tot_online':  Sum(F('OnLine'))}
        filters = ['Check1__date','Cell_id', 'Cell__Name', 'Cell__CellID', 'Cell__Plant']
        orders = ['-Check1__date','Cell__Plant', 'Cell__Name', 'Cell__CellID']
        qs = queryset.values(*filters).annotate(**metrics).order_by(*orders)
        for item in qs:
            if item['tot_online'] is not None:
                item['tot_online'] = sec2TmStr(item['tot_online'])
        return qs

    def changelist_view(self, request, extra_context=None):
        return changelist_view(self, request, extra_context)

@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ['Plant','Name','CellID','Type','Create','OnLineStr','WorkTMStr','status']
    ordering = ['Plant','Name','CellID']

    list_displayHead = ['车间','机台','机台编号','分类','创建日期','在线时长','作业时长','状态']
    metrics = filters = orders = ''
    def appendXmlWs(self, ws, queryset):
        i = 0
        for obj in queryset:
            i = i + 1
            ws.append([i, obj.Plant, obj.Name, obj.CellID, obj.Type, obj.Create, sec2TmStr(obj.OnLine), sec2TmStr(obj.WorkTM), obj.get_Alarmi_display()])
    actions = [export_as_xml]

@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_filter = ['Cell_id', RecordFilter]
    actions = [export_as_xml]
    change_list_template = 'amfui/record_change_list.html'
    
    list_displayHead = ['日期','车间','机台','机台编号','工单编号','开机时长','作业时长','待机时长','完成工件','预估剩余']
    def appendXmlWs(self, ws, queryset):
        i = 0
        for obj in queryset:
            i = i + 1
            ws.append( [i,obj['StartTime__date'], obj['Cell__Plant'], obj['Cell__Name'], obj['Cell__CellID'], 
                       obj['WorkSheet_id'], obj['tot_poweron'], obj['tot_workTM'], obj['tot_idleTM'], obj['tot_parts'], obj['min_estiTM']])

    def get_select_queryset(self, request, queryset):
        metrics = {
            'tot_adjustTM': Sum('PowerOnSec',filter=Q(Mode='调校模式')),
            'tot_poweron':  Sum('PowerOnSec'),
            'tot_workTM':   Sum('WorkingSec',filter=Q(Mode='普通模式')),
            'tot_idleTM':   Sum('IdleTMSec',filter=Q(Mode='普通模式')),
            'min_estiTM':   Min('EstimatedSec',filter=Q(Mode='普通模式')),
            'tot_parts':    Sum('FinishParts',filter=Q(Mode='普通模式')),
            }
        filters = ['StartTime__date','Cell__Plant','Cell__Name','Cell__CellID','WorkSheet_id']
        orders = ['-StartTime__date','Cell__Plant','Cell__Name','Cell__CellID','WorkSheet_id']
        qs = queryset.values(*filters).annotate(**metrics).order_by(*orders)
        for item in qs:
            for key in ['tot_poweron','tot_workTM','tot_idleTM','tot_adjustTM','min_estiTM']:
                if item[key] is not None:
                    item[key] = sec2TmStr(item[key])
        return qs

    def changelist_view(self, request, extra_context=None):
        return changelist_view(self, request, extra_context)

@admin.register(RecordManage)
class RecordManageAdmin(admin.ModelAdmin):
    #list_filter = ['Cell_id', RecordFilter]
    actions = [export_as_xml]
    change_list_template = 'amfui/worksheet_change_list.html'

    list_displayHead = ['工单编号', '车间','机台','机台编号','开机时长','作业时长','待机时长','完成工件','预估剩余', '工单状态']
    def appendXmlWs(self, ws, queryset):
        i = 0
        for obj in queryset:
            i = i + 1
            ws.append([i,obj['WorkSheet_id'], obj['Cell__Plant'], obj['Cell__Name'], obj['Cell__CellID'], 
                obj['tot_poweron'], obj['tot_workTM'], obj['tot_idleTM'], obj['tot_parts'], obj['min_estiTM'], obj['WorkSheet__Status']])

    def get_select_queryset(self, request, queryset):
        metrics = {
            'tot_adjustTM': Sum('PowerOnSec',filter=Q(Mode='调校模式')),
            'tot_poweron':  Sum('PowerOnSec'),
            'tot_workTM':   Sum('WorkingSec',filter=Q(Mode='普通模式')),
            'tot_idleTM':   Sum('IdleTMSec',filter=Q(Mode='普通模式')),
            'min_estiTM':   Min('EstimatedSec',filter=Q(Mode='普通模式')),
            'tot_parts':    Sum('FinishParts',filter=Q(Mode='普通模式')),
            }
        filters = ['Cell__Plant','Cell__Name','Cell__CellID','WorkSheet_id', 'WorkSheet__Status']
        orders = ['WorkSheet__Status', 'Cell__Plant','Cell__Name','Cell__CellID','WorkSheet_id']
        qs = queryset.values(*filters).annotate(**metrics).order_by(*orders)
        qs = list(qs)
        for item in qs:
            for key in ['tot_poweron','tot_workTM','tot_idleTM','tot_adjustTM','min_estiTM']:
                if item[key] is not None:
                    item[key] = sec2TmStr(item[key])
        return qs

    def changelist_view(self, request, extra_context=None):
        return changelist_view(self, request, extra_context)

#@admin.register(Alarmi)
class AlarmiAdmin(admin.ModelAdmin):
    list_display = ['Id','AllarmString','TypeID','Description_Id',]
    ordering = ['Id']

#@admin.register(LiveStateManage)
class LiveStateManageAdmin(admin.ModelAdmin):
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

#@admin.register(WorkSheet)
class WorkSheetAdmin(admin.ModelAdmin):
    list_display = ['Id','Cell__CellID','Order_id','Product_id','Status','ProcessID','FinishParts','ReqParts','AddReqParts',]

#@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['Id','Status','Colour','Product_id','ReqParts',]

    

