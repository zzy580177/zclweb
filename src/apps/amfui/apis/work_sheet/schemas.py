from ninja import ModelSchema
from apps.amfui.models import *

from typing import List, Optional
from apps.amfui.apis.cell.schemas import CellOut, CellIdInfoOut

class WorkSheetIn(ModelSchema):
    
    Cell_id: int
    
    Order_id: str
    

    class Meta:
        model = WorkSheet
        fields = ['Product_id', 'Status', 'ProcessID', 'FinishParts', 'ReqParts', 'AddReqParts', ]


class WorkSheetOut(ModelSchema):
    Cell: Optional[CellOut]
    class Meta:
        model = WorkSheet
        fields = ['Id', 'Cell', 'Order', 'Product_id', 'Status', 'ProcessID', 'FinishParts', 'ReqParts', 'AddReqParts', ]

class WorkSheetCellOut(ModelSchema):
    Cell: Optional[CellIdInfoOut]
    class Meta:
        model = WorkSheet
        fields = ['Id', 'Cell' ]

class WorkSheetRecordOut(ModelSchema):
    req_parts: Optional[int] = None
    idle_sec: Optional[int] = None
    power_on_sec: Optional[int] = None
    working_sec: Optional[int] = None
    estimated_sec: Optional[int] = None
    class Meta:
        model = WorkSheet
        fields = ['Id', 'Order', 'Product_id', 'ProcessID', 'Status', 'FinishParts', ]

