from ninja import ModelSchema
from apps.amfui.models import *
from typing import List, Optional
from apps.amfui.apis.alarmi.schemas import AlarmiOut

from django.db.models import DateTimeField


class StatoIn(ModelSchema):
    
    Cell_id: int
    
    WorkSheet_id: str
    
    Alarmi_id: int
    

    class Meta:
        model = Stato
        fields = ['DataTime', 'Stato', 'TimeSpan', ]


class StatoOut(ModelSchema):
    Alarmi: Optional[AlarmiOut] = None
    stop_time: Optional[str] = None
    class Meta:
        model = Stato
        fields = ['id', 'Cell', 'WorkSheet', 'DataTime', 'Stato', 'TimeSpan', ]
    
    @staticmethod    
    def resolve_Alarmi(obj):
        try:
            if obj.Alarmi:
                return Alarmi.from_orm(obj.Alarmi)
            return None
        except Alarmi.DoesNotExist:
            return None
