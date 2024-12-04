from django.contrib import admin
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _
from .models import *
from django.db.models import Min, Sum, Q,F,Value, Avg
import calendar

from datetime import datetime
from django.http import HttpRequest, HttpResponse
from openpyxl import Workbook

dayFilter = (('0', u'当天'),('1', u'本周'),('2', u'本月'), ('3', u'上个月'))
class MonthFilter(admin.SimpleListFilter):
    title = _('month') # type: ignore
    parameter_name = 'month'
 
    def lookups(self, request, model_admin):
        # 获取当前年份
        day = self.value()
        if day is None:
            year = datetime.now().year
        current_month = datetime.now().month
        date_field = 'StartTime'
        if model_admin.__class__.__name__ == 'RecordAdmin':
            date_field = 'StartTime'
        elif model_admin.__class__.__name__ == 'LiveStateAdmin':
            date_field = 'Check1'
        earliest_date = model_admin.model.objects.aggregate(Min(date_field))[f'{date_field}__min']     
        earliest_month = 1
        if earliest_date:
            year = earliest_date.year
            earliest_month = earliest_date.month            
        return [(f'{year}-{i:02d}', f'{year}年{i}月') for i in range(current_month, earliest_month-1, -1)]
 
    def queryset(self, request, queryset):
        # 获取选中的月份
        value = self.value()
        if value is None:
            value = datetime.now().strftime('%Y-%m-%d')
            return queryset.filter(Q(StartTime__gte=value) )
        elif value:
            # 构造查询条件，筛选出该月份的所有数据
            year, month = value.split('-')
            end_date = f'{year}-{month}-{ calendar.monthrange(int(year), int(month))[1]}'
            start_date = f'{year}-{month}-01'
            return queryset.filter(
                Q(StartTime__gte=start_date) & Q(StartTime__lt=end_date)
            )
        return queryset

class LFMonthFilter(MonthFilter):
    def queryset(self, request, queryset):
        # 获取选中的月份
        value = self.value()
        if value is None:
            value = datetime.now().strftime('%Y-%m-%d')
            return queryset.filter(Q(Check1__gte=value) )
        elif value:
            # 构造查询条件，筛选出该月份的所有数据
            year, month = value.split('-')
            end_date = f'{year}-{month}-{ calendar.monthrange(int(year), int(month))[1]}'
            start_date = f'{year}-{month}-01'
            return queryset.filter(
                Q(Check1__gte=start_date) & Q(Check1__lt=end_date)
            )
        return queryset

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
    list_filter = ['Cell_id', 'Check1']
    actions = [export_as_xml]
    change_list_template = 'amfui/livestate_change_list.html'
    list_displayHead = ['日期','车间','机台','机台编号','在线时长', '开机时长','掉线率', '作业时长', '待机时长','调机时长']
    def appendXmlWs(self, ws, queryset):
        i = 0
        for obj in queryset:
            i = i + 1
            ws.append([i, obj['Day'], obj['Cell__Plant'], obj['Cell__Name'], obj['Cell__CellID'], 
                       obj['tot_online'], obj['tot_powerOn'], obj['offline_rate'], obj['tot_workTM'], obj['tot_idleTM'], obj['tot_adjustTM'],])

    def get_queryset(self, request):
        from django.utils import timezone
        # 获取当前月份的开始和结束日期
        start_of_month = timezone.now().replace(day=1)
        end_of_month = timezone.now().replace(day=28) + timezone.timedelta(days=4)  # 加4天以确保月末
        queryset = super().get_queryset(request)
        return queryset.filter(Check1__range=(start_of_month, end_of_month))

    def get_select_queryset(self, request, queryset):
        metrics = {'offline_rate':Value(""), 'Day':F('Check1__date'),'tot_online':  Sum(F('OnLine')), 'tot_powerOn': Value(0), 'tot_workTM': Value(0), 'tot_idleTM': Value(0), 'tot_adjustTM': Value(0),}
        filters = ['Cell_id', 'Cell__Name', 'Cell__CellID', 'Cell__Plant']
        orders = ['-Check1__date','Cell__Plant', 'Cell__Name', 'Cell__CellID']
        qs = queryset.values(*filters).annotate(**metrics).order_by(*orders)

        metrics = {'offline_rate':Value(""),'Day':F('StartTime__date'),'tot_online': Value(0),'tot_powerOn': Sum(F('PowerOnSec')), 'tot_workTM': Sum(F('WorkingSec')), 'tot_idleTM': Sum(F('IdleTMSec')), 'tot_adjustTM': Sum('PowerOnSec',filter=Q(Mode='调校模式')),}
        filters = ['Cell_id', 'Cell__Name', 'Cell__CellID', 'Cell__Plant']
        orders = ['-StartTime__date','Cell__Plant', 'Cell__Name', 'Cell__CellID']
        index = 0
        for item in qs:
            try:
                related_obj = Record.objects.all().values(*filters).annotate(**metrics).order_by(*orders).filter(Q(Cell_id=item['Cell_id'])&Q(Day=item['Day'])).first()
                if (related_obj):
                    item['tot_powerOn'] = related_obj['tot_powerOn']
                    item['tot_workTM'] = related_obj['tot_workTM']
                    item['tot_idleTM'] = related_obj['tot_idleTM']
                    item['tot_adjustTM'] = related_obj['tot_adjustTM']
                    if item['tot_online'] is  None:
                        item['tot_online'] = 0;
                    if ((item['tot_online'] is not None) & (item['tot_powerOn'] is not None) & (item['tot_powerOn'] > 0)):
                        if item['tot_powerOn'] > 60*24*60:
                            item['tot_powerOn'] = 60*24*60
                        item['tot_online'] = item['tot_powerOn'] if (item['tot_powerOn'])< float(item['tot_online']) else item['tot_online']
                        item['offline_rate'] = round(((item['tot_powerOn']-item['tot_online'])/item['tot_powerOn'])*100,1)
                    related_obj = None
            except Record.DoesNotExist:
                pass
            for key in ['tot_powerOn','tot_workTM','tot_idleTM','tot_adjustTM', 'tot_online']:
                item[key] = None if item[key] == 0 else item[key]
                if item[key] is not None:
                    if item[key] > 24*60*60:
                        item[key] = 24*60*60
                    item[key] = sec2TmStr(item[key])
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
            ws.append([i, obj.Plant, obj.Name, obj.CellID, obj.Type, obj.Create, sec2TmStr(obj.OnLine), sec2TmStr(obj.WorkTM), obj.get_Stato_display()])
    actions = [export_as_xml]

@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_filter = ['Cell_id','StartTime']
    actions = [export_as_xml]
    change_list_template = 'amfui/record_change_list.html'
    
    list_displayHead = ['日期','车间','机台','机台编号','订单编号','叠加订单号','款号','开机时长','作业时长','待机时长','调机时间','完成工件','预估剩余']
    def appendXmlWs(self, ws, queryset):
        i = 0
        for obj in queryset:
            i = i + 1
            ws.append( [i,obj['StartTime__date'], obj['Cell__Plant'], obj['Cell__Name'], obj['Cell__CellID'], 
                       obj['WorkSheet__Order_id'],obj['WorkSheet__Order__Colour'], obj['WorkSheet__Order__Product_id'], obj['tot_poweron'], obj['tot_workTM'], 
                       obj['tot_idleTM'],obj['tot_adjustTM'], obj['tot_parts'], obj['min_estiTM']])
    def get_queryset(self, request):
        from django.utils import timezone
        # 获取当前月份的开始和结束日期
        start_of_month = timezone.now().replace(day=1)
        end_of_month = timezone.now().replace(day=28) + timezone.timedelta(days=4)  # 加4天以确保月末
        queryset = super().get_queryset(request)
        return queryset.filter(StartTime__range=(start_of_month, end_of_month))

    def get_select_queryset(self, request, queryset):
        self.list_displayHead[12] = '预估剩余(%.1fH/Day)'% getDailyWorkTime(request.user)
        metrics = {
            'tot_adjustTM': Sum('PowerOnSec',filter=Q(Mode='调校模式')),
            'tot_poweron':  Sum('PowerOnSec'),
            'tot_workTM':   Sum('WorkingSec',filter=Q(Mode='普通模式')),
            'tot_idleTM':   Sum('IdleTMSec',filter=Q(Mode='普通模式')),
            'min_estiTM':   Min('EstimatedSec',filter=Q(Mode='普通模式'))*24/getDailyWorkTime(request.user),
            'tot_parts':    Sum('FinishParts',filter=Q(Mode='普通模式')),
            }
        filters = ['StartTime__date','Cell__Plant','Cell__Name','Cell__CellID','WorkSheet_id','WorkSheet__Order_id','WorkSheet__Order__Product_id', 'WorkSheet__Order__Colour']
        orders = ['-StartTime__date','Cell__Plant','Cell__Name','Cell__CellID','WorkSheet_id']
        qs = queryset.exclude(Q(WorkSheet_id='未绑定工单')).values(*filters).annotate(**metrics).order_by(*orders)
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

    list_displayHead = ['订单编号','叠加订单号','款号', '车间','机台','机台编号','开机时长','作业时长','待机时长','调机时间','计划工件','完成工件','预估剩余', '工单状态']
    def appendXmlWs(self, ws, queryset):
        i = 0
        for obj in queryset:
            i = i + 1
            ws.append([i,obj['WorkSheet__Order_id'],obj['WorkSheet__Order__Colour'],obj['WorkSheet__Order__Product_id'], obj['Cell__Plant'], obj['Cell__Name'], obj['Cell__CellID'], 
                obj['tot_poweron'], obj['tot_workTM'], obj['tot_idleTM'], obj['tot_adjustTM'],obj['WorkSheet__ReqParts']+obj['WorkSheet__AddReqParts'],  obj['WorkSheet__FinishParts'], obj['min_estiTM'], 
                obj['WorkSheet__Status']])

    def get_select_queryset(self, request, queryset):
        self.list_displayHead[12] = '预估剩余(%.1fH/Day)'% getDailyWorkTime(request.user)
        metrics = {
            'tot_adjustTM': Sum('PowerOnSec',filter=Q(Mode='调校模式')),
            'tot_poweron':  Sum('PowerOnSec'),
            'tot_workTM':   Sum('WorkingSec',filter=Q(Mode='普通模式')),
            'tot_idleTM':   Sum('IdleTMSec',filter=Q(Mode='普通模式')),
            'min_estiTM':   Min('EstimatedSec',filter=Q(Mode='普通模式'))*24/getDailyWorkTime(request.user),
            'tot_parts':    Sum('FinishParts',filter=Q(Mode='普通模式')),
            }
        filters = ['Cell__Plant','Cell__Name','Cell__CellID','WorkSheet_id', 'WorkSheet__Status','WorkSheet__Order_id',
                   'WorkSheet__Order__Product_id', 'WorkSheet__Order__Colour','WorkSheet__ReqParts','WorkSheet__AddReqParts','WorkSheet__FinishParts']
        orders = ['WorkSheet__Status', 'Cell__Plant','Cell__Name','Cell__CellID','WorkSheet_id']
        qs = queryset.exclude(Q(WorkSheet_id='未绑定工单')).values(*filters).annotate(**metrics).order_by(*orders)
        for item in qs:
            for key in ['tot_poweron','tot_workTM','tot_idleTM','tot_adjustTM','min_estiTM','WorkSheet__ReqParts']:
                if (key == 'WorkSheet__ReqParts'):
                    item[key] = item[key] + item['WorkSheet__AddReqParts'] 
                elif item[key] is not None:
                    item[key] = sec2TmStr(item[key])
        return qs

    def changelist_view(self, request, extra_context=None):
        return changelist_view(self, request, extra_context)

#@admin.register(Alarmi)
class AlarmiAdmin(admin.ModelAdmin):
    list_display = ['Id','AlarmString','TypeID','Description_Id',]
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


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):    
    list_display = ['Id', 'Colour', 'Product_id', 'ReqParts', 'Status']
    list_editable = ['Colour', 'Product_id']
    
    def save_model(self, request, obj, form, change):
        if change:
            # Update existing record
            Order.objects.filter(Id=form.cleaned_data['id'].Id).update(
                Colour=form.cleaned_data['Colour'],
                Product_id=form.cleaned_data['Product_id'])
        else:
            obj.save()
            
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        orderId = 0
        if request.method == "POST":
            for key, value in request.POST.items():
                if key.startswith('form-') and '-' in key:
                    row_id = key.split('-')[1]
                    if row_id.isdigit():
                        field = key.split('-')[2]
                        if field in ['id']:
                            orderId = value
                        if field in ['Colour', 'Product_id' ,'Id']:
                            Order.objects.filter(id=orderId).update(**{field: value})
        return super().changelist_view(request, extra_context)
    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request)
    
 
class ChildModel2Inline(admin.TabularInline):
    model = Cell
    extra = 1  # 可以根据需要设置额外的行数


    

