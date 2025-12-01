from ninja import ModelSchema
from apps.c_gongyi.models import *
from typing import List, Optional


class MaterialParmIn(ModelSchema):
    
    material_number: str
    version: str
    cost: Optional[str] = None   

    class Meta:
        model = MaterialParm
        fields = ['size', 'stuff', 'cost', 'surface', 'description', ]


class MaterialParmOut(ModelSchema):
    class Meta:
        model = MaterialParm
        fields = ['id', 'bom_ver', 'size', 'stuff', 'cost', 'surface', 'description', ]
