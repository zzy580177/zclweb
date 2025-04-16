from ninja import ModelSchema
from apps.bmui.models import *


class BOMLevelIn(ModelSchema):
    
    BOM_id: 
    

    class Meta:
        model = BOMLevel
        fields = ['Level', ]


class BOMLevelOut(ModelSchema):
    class Meta:
        model = BOMLevel
        fields = ['Id', 'BOM', 'Level', ]
