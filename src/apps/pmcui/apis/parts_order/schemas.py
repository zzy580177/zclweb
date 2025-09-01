from ninja import ModelSchema, Schema
from decimal import Decimal
from typing import Optional, List
from apps.pmcui.models import *
from apps.bmui.apis.material.schemas import MaterialFullOut, MaterialOut
from apps.pmcui.apis.p_order.schemas import POrderOut

class PartsOrderIn(ModelSchema):
    POrder_id: str
    FNumber: str
    FId: str
    FModel: Optional[str]
    FName:  Optional[str]
    Name:  Optional[str]
    Id: Optional[str]

    class Meta:
        model = PartsOrder
        fields = [ 'Status', 'Quantity', 'Description']

class PartsOrderOut(ModelSchema):
    POrder_id: Optional[str] = None
    Quantity: Optional[float] = None
    class Meta:
        model = PartsOrder
        fields = ['CreateTime', 'UpdateTime', 'IsDelete', 'IsActive', 'Id', 'POrder', 'Part',  'Status', 'DeadLine', 'Cost', 'Quantity', 'Description']
    @staticmethod
    def resolve_POrder_id(obj):
        return obj.POrder.OrderId if obj.POrder else None

class PartsOrderOut2(ModelSchema):
    Quantity: Optional[float] = None
    Cost: Optional[float] = None
    Part: Optional[MaterialFullOut]
    POrder: Optional[POrderOut]
    POrder_id: Optional[str] = None
    
    class Config:
        orm_mode = True
        
    class Meta:
        model = PartsOrder
        fields = ['CreateTime', 'UpdateTime', 'IsDelete', 'IsActive', 'Id', 'POrder', 'Part',  'Status', 'DeadLine', 'Cost', 'Quantity', 'Description']
    @staticmethod
    def resolve_POrder_id(obj):
        return obj.POrder.OrderId if obj.POrder else None

class PartsOrderAdminIn(ModelSchema):
    Part_FNumber: str
    Part_FModel: str
    Part_FName: str
    Part_FUnit_Name: str
    POrder_id: str

    class Meta:
        model = PartsOrder
        fields = ['Status', 'Quantity', 'Description']

class PartsOrderAdminOut(ModelSchema):
    Part: Optional[MaterialFullOut]
    Quantity: Optional[float] = None
    Cost: Optional[float] = None

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None
        }

    class Meta:
        model = PartsOrder
        fields = ['Status', 'POrder', 'Part', 'Quantity', 'Description']

class PartNumOrderAdminIn(ModelSchema):
    Part_FNumber: str
    POrder_id: str
    class Meta:
        model = PartsOrder
        fields = ['Status','Quantity', 'Description']
