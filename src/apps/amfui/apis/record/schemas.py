from ninja import ModelSchema
from apps.amfui.models import *


class RecordIn(ModelSchema):
    
    Cell_id: int
    
    WorkSheet_id: str
    

    class Meta:
        model = Record
        fields = ['StartTime', 'StopTime', 'Status', 'Mode', 'FinishParts', 'IdleTMSec', 'PowerOnSec', 'WorkingSec', 'EstimatedSec', ]


class RecordOut(ModelSchema):
    class Meta:
        model = Record
        fields = ['id', 'Cell', 'WorkSheet', 'StartTime', 'StopTime', 'Status', 'Mode', 'FinishParts', 'IdleTMSec', 'PowerOnSec', 'WorkingSec', 'EstimatedSec', ]
