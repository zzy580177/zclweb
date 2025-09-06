from ninja import ModelSchema
from apps.a_wuliao.models import *


class MaterialIn(ModelSchema): 
    unit: str    

    class Meta:
        model = Material
        fields = ['material_id', 'number', 'name', 'helpcode', 'model', 'source', 'description']


class MaterialOut(ModelSchema):
    class Meta:
        model = Material
        fields = ['material_id', 'group', 'number', 'name', 'helpcode', 'model', 'unit', 'source', 'description', ]

class MaterialSampleOut(ModelSchema):
    material_model: str
    material_number: str
    material_name: str
    class Meta:
        model = Material
        fields = ['material_id',  ]
