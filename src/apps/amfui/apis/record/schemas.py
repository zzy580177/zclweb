from ninja import ModelSchema
from apps.amfui.models import *
from typing import List, Optional
from apps.amfui.apis.work_sheet.schemas import WorkSheetCellOut, WorkSheetOut
from apps.amfui.apis.cell.schemas import CellIdInfoOut

class RecordIn(ModelSchema):
    
    Cell_id: int        

    class Meta:
        model = Record
        fields = ['StartTime', 'StopTime', 'Status', 'Mode', 'FinishParts', 'IdleTMSec', 'PowerOnSec', 'WorkingSec', 'EstimatedSec', ]


from datetime import date
from ninja import Schema
from apps.amfui.models import Cell


class RecordOut(ModelSchema):
    WorkSheet: Optional[WorkSheetOut]
    date_only: Optional[date] = None
    cell: Optional[CellIdInfoOut] = None
    
    @staticmethod
    def resolve_cell(obj):
        if hasattr(obj, 'cell') and obj.cell:
            return f"{obj.cell.Name} {obj.cell.CellID}"
        return None

    class Meta:
        model = Record
        fields = ['id', 'WorkSheet', 'StartTime', 'StopTime', 'Status', 'Mode', 'FinishParts', 'IdleTMSec', 'PowerOnSec', 'WorkingSec', 'EstimatedSec']


class RecordAggregatedOut(Schema):
    date_only: date
    cell_str: Optional[str] = None  # Will be resolved to a string representation
    finish_sum: Optional[int] = None
    idle_sum: Optional[int] = None
    poweron_sum: Optional[int] = None
    working_sum: Optional[int] = None
    adjust_sum: Optional[int] = None
    estimated_sum: Optional[int] = None
    online_sum: Optional[int] = None

