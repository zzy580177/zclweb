from ninja import ModelSchema
from apps.bmui.models import *


class BOMIn(ModelSchema):
    
    Material_id: int
    

    class Meta:
        model = BOM
        fields = ['CreateTime', 'UpdateTime', 'IsDelete', 'IsActive', 'Quantity', 'Version', 'Description', ]


class BOMOut(ModelSchema):
    class Meta:
        model = BOM
        fields = ['id', 'CreateTime', 'UpdateTime', 'IsDelete', 'IsActive', 'Material', 'Quantity', 'Version', 'Description', ]
