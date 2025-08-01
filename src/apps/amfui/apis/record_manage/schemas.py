from ninja import ModelSchema
from apps.amfui.models import *
from typing import List, Optional
from apps.amfui.apis.work_sheet.schemas import WorkSheetOut

class RecordManageIn(ModelSchema):
    
    Cell_id: int
    
    WorkSheet_id: str
    

    class Meta:
        model = RecordManage
        fields = ['StartTime', 'StopTime', 'Status', 'Mode', 'FinishParts', 'IdleTMSec', 'PowerOnSec', 'WorkingSec', 'EstimatedSec', ]


class RecordManageOut(ModelSchema):
    WorkSheet: Optional[WorkSheetOut]
    class Meta:
        model = RecordManage
        fields = ['id',  'WorkSheet', 'StartTime', 'StopTime', 'Status', 'Mode', 'FinishParts', 'IdleTMSec', 'PowerOnSec', 'WorkingSec', 'EstimatedSec', ]
