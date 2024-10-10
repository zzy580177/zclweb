from ninja import ModelSchema
from apps.amfui.models import *


class CellIn(ModelSchema):
    
    Alarmi_id: str
    

    class Meta:
        model = Cell
        fields = ['CellID', 'Plant', 'Name', 'Type', 'IP', 'Create', 'OnLine', 'WorkTM', ]


class CellOut(ModelSchema):
    class Meta:
        model = Cell
        fields = ['id', 'CellID', 'Plant', 'Name', 'Type', 'Alarmi', 'IP', 'Create', 'OnLine', 'WorkTM', ]
