from ninja import ModelSchema
from typing import Optional
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
        fields = ['CreateTime', 'UpdateTime', 'IsDelete', 'IsActive', 'FId', 'FGroup', 'FNumber', 'FName', 'FHelpCode', 'FModel', 'FUnit', 'FSource', 'FDescription', ]
