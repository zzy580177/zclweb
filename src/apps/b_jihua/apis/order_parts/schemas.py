from typing import Optional, List

from ninja import ModelSchema
from apps.b_jihua.models import *
from apps.a_wuliao.models import BomVersion


class OrderPartsIn(ModelSchema):
    
    order: Optional[str] = None
    material: Optional[str] = None
    status: Optional[str] = None
    deadline: Optional[str] = None
    delivery_day: Optional[str] = None
    quantity: Optional[str] = None  
    defectives: Optional[str] = None
    deliveries: Optional[str] = None
    cost: Optional[str] = None
    version: Optional[str] = None
    order_id: Optional[str] = None    
    material_id: Optional[str] = None
    material_number: Optional[str] = None
    material_name: Optional[str] = None
    material_model: Optional[str] = None
    material_unitname: Optional[str] = None
    id: Optional[str] = None

    class Meta:
        model = OrderParts
        fields = [ 'order', 'material', 'status', 'deadline', 'delivery_day', 'quantity', 'defectives', 'deliveries', 'cost', 'description',]

class OrderPartsOut(ModelSchema):
    material_number: str
    material_name: str
    material_model: str
    material_unit_name: str
    material_group_name: str
    material_id: int
    order_id: str
    version: Optional[str] = None
    history_versions: List[str] = None  
    class Meta:
        model = OrderParts
        fields = ['id', 'create_time', 'update_time', 'is_deleted', 'deleted_at', 'deleted_by', 'order', 'material', 'status', 'deadline', 'delivery_day', 'quantity', 'defectives', 'deliveries', 'cost', 'description', ]
    @staticmethod
    def resolve_order_id(obj):
        if hasattr(obj, 'order') and obj.order:
            return obj.order.order_id
        return None

    @staticmethod
    def resolve_material_number(obj):
        if hasattr(obj, 'material') and obj.material:
            return obj.material.number
        return None
    @staticmethod
    def resolve_material_name(obj):
        if hasattr(obj, 'material') and obj.material:
            return obj.material.name
        return None
    @staticmethod
    def resolve_material_model(obj):
        if hasattr(obj, 'material') and obj.material:
            return obj.material.model
        return None
    @staticmethod
    def resolve_material_unit_name(obj):
        if hasattr(obj, 'material') and obj.material and hasattr(obj.material, 'unit') and obj.material.unit:
            return obj.material.unit.name
        return None
    @staticmethod
    def resolve_material_group_name(obj):
        if hasattr(obj, 'material') and obj.material and hasattr(obj.material, 'group') and obj.material.group:
            return obj.material.group.name
        return None
    
    @staticmethod
    def resolve_history_versions(obj):
        if hasattr(obj, 'material') and obj.material:
            return [ver.version for ver in BomVersion.objects.filter(material = obj.material).order_by('-create_time')]
        return None