from ninja import ModelSchema
from typing import Optional, List
from apps.bmui.models import *
from apps.bmui.apis.attribute.schemas import AttributeOut
from apps.bmui.apis.material_group.schemas import MaterialGroupOut

class MaterialIn(ModelSchema):
    
    FGroup_id: int
    
    FUnit_id: int
    

    class Meta:
        model = Material
        fields = ['CreateTime', 'UpdateTime', 'IsDelete', 'IsActive', 'FNumber', 'FName', 'FHelpCode', 'FModel', 'FSource', 'FDescription', ]


class MaterialOut(ModelSchema):
    FUnit: Optional[AttributeOut]
    FGroup: Optional[MaterialGroupOut]
    class Config:
        orm_mode = True
    class Meta:
        model = Material
        fields = ['CreateTime', 'UpdateTime', 'IsDelete', 'IsActive', 'FId', 'FGroup', 'FNumber', 'FName', 'FHelpCode', 'FModel','FParent', 'FUnit', 'FSource', 'FDescription', ]


class MaterialSampleOut(ModelSchema):   
    unit: Optional[str] = None
    class Config:
        orm_mode = True
    class Meta:
        model = Material
        fields = [ 'IsDelete', 'IsActive', 'FId', 'FNumber', 'FName', 'FHelpCode', 'FModel','FSource', 'FDescription', ]
    
    @staticmethod
    def resolve_unit(obj):
        if obj.FUnit is None:
            return None
        return getattr(obj.FUnit, 'Name', None)


class MaterialFullOut(ModelSchema):
    FUnit: Optional[AttributeOut]
    FGroup: Optional[MaterialGroupOut]
    sub_parts: Optional[List[MaterialSampleOut]] = None
    class Config:
        orm_mode = True
    class Meta:
        model = Material
        fields = ['CreateTime', 'UpdateTime', 'IsDelete', 'IsActive', 'FId', 'FGroup', 'FNumber', 'FName', 'FHelpCode', 'FModel','FParent', 'FUnit', 'FSource', 'FDescription', ]
