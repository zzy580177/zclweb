from ninja import ModelSchema, Schema
from apps.a_wuliao.models import *
from typing import List, Optional


class BomVersionIn(ModelSchema):
    base: Optional[str] =None
    material_name: str
    material_number: str
    material_model: str    
    p_material: Optional[str] = None

    class Meta:
        model = BomVersion
        fields = ['version', 'change_reason', 'status',]


class BomVersionOut(ModelSchema):
    material_id: str
    material_name: str
    material_number: str
    material_model: str
    
    class Meta:
        model = BomVersion
        prefetch_related = ['material']
        fields = ['version', 'base', 'change_reason', 'status', ]
    @staticmethod
    def resolve_material_id(obj):
        if obj.material is None:
            return None
        result = getattr(obj.material, 'material_id', None)
        return str(result)
    @staticmethod
    def resolve_material_name(obj):
        if obj.material is None:
            return None
        return getattr(obj.material, 'name', None)
    @staticmethod
    def resolve_material_number(obj):
        if obj.material is None:
            return None
        return getattr(obj.material, 'number', None)
    @staticmethod
    def resolve_material_model(obj):
        if obj.material is None:
            return None
        return getattr(obj.material, 'model', None)

class BomVersionListOut(ModelSchema):
    history_versions: List[str] = None   
    material_name: str
    material_number: str
    material_model: str
    
    class Meta:
        model = BomVersion
        fields = ['change_reason', 'status', ]
    @staticmethod
    def resolve_material_name(obj):
        if obj.material is None:
            return None
        return getattr(obj.material, 'name', None)
    @staticmethod
    def resolve_material_number(obj):
        if obj.material is None:
            return None
        return getattr(obj.material, 'number', None)
    @staticmethod
    def resolve_material_model(obj):
        if obj.material is None:
            return None
        return getattr(obj.material, 'model', None)
    @staticmethod
    def resolve_history_versions(obj):
        versions = BomVersion.objects.filter(material=obj.material).order_by('-create_time').values_list('version', flat=True)
        return list(versions)

    