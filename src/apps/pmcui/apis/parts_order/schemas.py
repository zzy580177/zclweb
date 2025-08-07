from ninja import ModelSchema, Schema
from typing import Optional, List
from apps.pmcui.models import *
from apps.bmui.apis.material.schemas import MaterialFullOut, MaterialOut
from apps.pmcui.apis.p_order.schemas import POrderOut

class PartsOrderIn(ModelSchema):
    POrder_id: str
    Part_id: int

    class Meta:
        model = PartsOrder
        fields = ['CreateTime', 'UpdateTime', 'IsDelete', 'IsActive', 'Idex', 'Status', 'DeadLine', 'Cost', 'Quantity', 'Description']

class PartsOrderOut(ModelSchema):
    Quantity: Optional[float] = None
    Cost: Optional[float] = None
    Part: Optional[MaterialFullOut]
    POrder: Optional[POrderOut]
    
    class Config:
        orm_mode = True
        
    class Meta:
        model = PartsOrder
        fields = ['CreateTime', 'UpdateTime', 'IsDelete', 'IsActive', 'Id', 'POrder', 'Part', 'Idex', 'Status', 'DeadLine', 'Cost', 'Quantity', 'Description']

