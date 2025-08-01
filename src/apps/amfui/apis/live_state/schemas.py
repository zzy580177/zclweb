from ninja import ModelSchema, Schema
from apps.amfui.models import *
from typing import List, Optional
from apps.amfui.apis.work_sheet.schemas import WorkSheetOut
from apps.amfui.apis.cell.schemas import CellIdInfoOut


class LiveStateIn(ModelSchema):
    
    Cell_id: int
    
    WorkSheet_id: str
    

    class Meta:
        model = LiveState
        fields = ['Check1', 'Check2', 'OnLine', ]


class LiveStateOut(ModelSchema):
    WorkSheet: Optional[WorkSheetOut] = None

    class Meta:
        model = LiveState
        fields = ['id', 'Cell', 'Check1', 'Check2', 'OnLine']

    @staticmethod
    def resolve_WorkSheet(obj):
        try:
            if obj.WorkSheet:
                return WorkSheetOut.from_orm(obj.WorkSheet)
            return None
        except WorkSheet.DoesNotExist:
            return None


from datetime import datetime

class DailyLiveStateOut(Schema):
    date_only: date
    online_sec: Optional[int] = None
    cell_str: Optional[str] = None

class AMFStateOut(Schema):
    max_check1: datetime
    cell_str: Optional[str] = None
    isOffLine: bool





