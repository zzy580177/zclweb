from django.contrib import admin
from django_starter.contrib.admin.tags import html_tags

from .models import *


@admin.register(Alarmi)
class AlarmiAdmin(admin.ModelAdmin):
    list_display = ['id','AllarmID','AllarmString','TypeID','Description_Id',]

    

@admin.register(LiveState)
class LiveStateAdmin(admin.ModelAdmin):
    list_display = ['id','Cell_id','Check1','Check2','TimeOff','OnLineSec']

    

@admin.register(LiveStateManage)
class LiveStateManageAdmin(admin.ModelAdmin):
    list_display = ['id','Cell_id','Check1','Check2','TimeOff','OnLine',]


@admin.register(Pezzi)
class PezziAdmin(admin.ModelAdmin):
    list_display = ['id','Cell_id','WorkSheetID','Data','DataTime','Pezzi','ReqPezzi','ResidPezzi','PieceTime','EstimatedTm','TotWorkTm',]
    

@admin.register(Stato)
class StatoAdmin(admin.ModelAdmin):
    list_display = ['id','Cell_id','WorkSheetID','Data','DataTime','Stato','Alarm',]

    

@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ['id','CellID','Plant','Name','Type','Status','IP','Create','OnLine','WorkTM',]

    

@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ['id','Cell_id','WorkSheetID','Date','StartTime','StopTime','Status','Mode','PowerOnTM','WorkingTM','FinishParts','IdleTMSec','PowerOnSec','WorkingSec',]


    

@admin.register(WorkSheet)
class WorkSheetAdmin(admin.ModelAdmin):
    list_display = ['id','Id','Cell_id','Order_id','WorkSheetID','OrderID','Status','ProcessID','FinishParts','ReqParts','AddReqParts',]


    

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id','OrderID','Status','Colour','ProductID','ReqParts',]


    

