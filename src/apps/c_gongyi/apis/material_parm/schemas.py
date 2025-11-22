from ninja import ModelSchema
from apps.c_gongyi.models import *


class MaterialParmIn(ModelSchema):
    
    bom_ver_id: int
    

    class Meta:
        model = MaterialParm
        fields = ['size', 'stuff', 'cost', 'surface', 'description', ]


class MaterialParmOut(ModelSchema):
    class Meta:
        model = MaterialParm
        fields = ['id', 'bom_ver', 'size', 'stuff', 'cost', 'surface', 'description', ]
