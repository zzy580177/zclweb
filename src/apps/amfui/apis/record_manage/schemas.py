from ninja import ModelSchema
from apps.amfui.models import *


class RecordManageIn(ModelSchema):
    
    Cell_id: int
    
    WorkSheet_id: str
    

    class Meta:
        model = RecordManage
        fields = ['StartTime', 'StopTime', 'Status', 'Mode', 'FinishParts', 'IdleTMSec', 'PowerOnSec', 'WorkingSec', 'EstimatedSec', ]


class RecordManageOut(ModelSchema):
    class Meta:
        model = RecordManage
        fields = ['id', 'Cell', 'WorkSheet', 'StartTime', 'StopTime', 'Status', 'Mode', 'FinishParts', 'IdleTMSec', 'PowerOnSec', 'WorkingSec', 'EstimatedSec', ]
