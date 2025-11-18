from ninja import ModelSchema
from apps.a_wuliao.models import *
from typing import List, Optional

class BomIn1(ModelSchema):   
    material_name: str
    material_number: str
    material_model: str    
    p_material: Optional[str] = None
    version: str

    class Meta:
        model = Bom
        fields = ['quantity', 'p_material', 'version']

class BomIn(ModelSchema):   
    class Meta:
        model = Bom
        fields = ['is_deleted', 'deleted_at', 'deleted_by', 'quantity', 'level', 'remark', ]


class BomOut(ModelSchema):
    class Meta:
        model = Bom
        fields = ['is_deleted', 'deleted_at', 'deleted_by', 'version', 'p_material', 'c_material', 'quantity', 'level', 'remark', ]
