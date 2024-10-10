from ninja import ModelSchema
from apps.amfui.models import *


class LiveStateIn(ModelSchema):
    
    Cell_id: int
    
    WorkSheet_id: str
    

    class Meta:
        model = LiveState
        fields = ['Check1', 'Check2', 'OnLine', ]


class LiveStateOut(ModelSchema):
    class Meta:
        model = LiveState
        fields = ['id', 'Cell', 'Check1', 'Check2', 'WorkSheet', 'OnLine', ]
