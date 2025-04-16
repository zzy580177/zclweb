from ninja import ModelSchema
from apps.bmui.models import *


class BOMIn(ModelSchema):
    
    Material_id: 
    
    ParentBOM_id: 
    

    class Meta:
        model = BOM
        fields = ['Quantity', ]


class BOMOut(ModelSchema):
    class Meta:
        model = BOM
        fields = ['Id', 'Material', 'Quantity', 'ParentBOM', ]
