from ninja import ModelSchema
from apps.a_wuliao.models import *
from typing import List, Optional
from apps.c_gongyi.models import Route
from apps.c_gongyi.apis.route.schemas import OrderRouteOut

class BomIn(ModelSchema):   
    material_name: Optional[str] = None
    material_number: Optional[str] = None
    material_model: Optional[str] = None        
    c_material: Optional[str] = None
    p_material: Optional[str] = None
    version: Optional[str] = None
    level: Optional[str] = None
    remark: Optional[str] = None

    class Meta:
        model = Bom
        fields = ['is_deleted', 'deleted_at', 'deleted_by', 'version', 'p_material', 'c_material', 'quantity', 'level', 'remark', ]


class BomOut(ModelSchema):
    class Meta:
        model = Bom
        fields = ['is_deleted', 'deleted_at', 'deleted_by', 'version', 'p_material', 'c_material', 'quantity', 'level', 'remark', ]


class SubBomOut(ModelSchema):
    material_id: Optional[int] = None
    material_name: Optional[str] = None
    material_number: Optional[str] = None
    material_model: Optional[str] = None   
    material_unit_name: Optional[str] = None
    version: Optional[str] = None
    class Meta:
        model = Bom
        fields = ['version', 'p_material', 'quantity', 'level', 'remark', ]
    
    @staticmethod
    def resolve_version(obj):
        if obj.version is None or obj.version.version is None:
            return None
        return getattr(obj.version,'version', None)
    
    @staticmethod
    def resolve_material_name(obj):
        if obj.version is None or obj.version.material is None:
            return None
        return getattr(obj.version.material, 'name', None)
    @staticmethod
    def resolve_material_number(obj):
        if obj.version is None or obj.version.material is None:
            return None
        return getattr(obj.version.material, 'number', None)
    @staticmethod
    def resolve_material_model(obj):
        if obj.version is None or obj.version.material is None:
            return None
        return getattr(obj.version.material, 'model', None)
    @staticmethod
    def resolve_material_unit_name(obj):
        if obj.version is None or obj.version.material is None or obj.version.material.unit is None:
            return None
        return getattr(obj.version.material.unit, 'name', None)
    @staticmethod
    def resolve_material_id(obj):
        if obj.version is None or obj.version.material is None:
            return None
        return getattr(obj.version.material, 'material_id', None)
