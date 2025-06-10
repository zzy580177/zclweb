from ninja import ModelSchema
from apps.bmui.models import *


class MaterialGroupIn(ModelSchema):
    
    FParent_id: int
    

    class Meta:
        model = MaterialGroup
        fields = ['FName', 'FNumber', 'FLevel', 'FClass', 'FGroupCode', 'FSubGroupCode', ]


class MaterialGroupOut(ModelSchema):
    class Meta:
        model = MaterialGroup
        fields = ['FId', 'FName', 'FParent', 'FNumber', 'FLevel', 'FClass', 'FGroupCode', 'FSubGroupCode', ]
