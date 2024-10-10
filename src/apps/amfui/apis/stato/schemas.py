from ninja import ModelSchema
from apps.amfui.models import *


class StatoIn(ModelSchema):
    
    Cell_id: int
    
    WorkSheet_id: str
    
    Alarmi_id: str
    

    class Meta:
        model = Stato
        fields = ['DataTime', 'Stato', 'TimeSpan', ]


class StatoOut(ModelSchema):
    class Meta:
        model = Stato
        fields = ['id', 'Cell', 'WorkSheet', 'DataTime', 'Stato', 'Alarmi', 'TimeSpan', ]
