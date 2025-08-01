from ninja import ModelSchema
from apps.amfui.models import *
from typing import List, Optional
from apps.amfui.apis.work_sheet.schemas import WorkSheetOut


class LiveStateManageIn(ModelSchema):
    
    Cell_id: int
    
    WorkSheet_id: str
    

    class Meta:
        model = LiveStateManage
        fields = ['Check1', 'Check2', 'OnLine', ]


class LiveStateManageOut(ModelSchema):    
    WorkSheet: Optional[WorkSheetOut]
    class Meta:
        model = LiveStateManage
        fields = ['id', 'Cell', 'Check1', 'Check2', 'WorkSheet', 'OnLine', ]
