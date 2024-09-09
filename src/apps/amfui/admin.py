from django.contrib import admin
from django_starter.contrib.admin.tags import html_tags

from .models import *


@admin.register(Alarmi)
class AlarmiAdmin(admin.ModelAdmin):
    list_display = ['AllarmID','AllarmString']
    list_display_links =  ['AllarmID','AllarmString']

@admin.register(LiveState)
class LiveStateAdmin(admin.ModelAdmin):
    list_display = ['Note_Id','CellaID','Plant','Check1','Check2']

@admin.register(Pezzi)
class PezziAdmin(admin.ModelAdmin):
    list_display = ['DataTime','Pezzi','ReqPezzi','ResidPezzi','EstimatedTm','WorkSheetID','CellaID']

@admin.register(Stato)
class StatoAdmin(admin.ModelAdmin):
    list_display = ['DataTime','get_Stato_display','Alarm','CellaID','Plant','WorkSheetID']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['OrderID','WorkSheetID','WorkStatus','Colour','Process','StytleNum','FinishParts','RequireParts','AddReqParts','CellaID','Plant',]

@admin.register(OrderHistory)
class OrderHistoryAdmin(admin.ModelAdmin):
    list_display = ['Mode','WorkSheetID','StartTime','StopTime','WorkingTM','FinishParts','CellaID','Plant',]


    

