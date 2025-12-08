from typing import Optional, List

from ninja import ModelSchema
from apps.b_jihua.models import *
from apps.a_wuliao.models import BomVersion
from apps.c_gongyi.apis.route.schemas import OrderRouteOut
from apps.c_gongyi.models import Route
from apps.d_paichan.models import ProductionPlan


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
    


class OrderPartOut(ModelSchema):
    material_number: str    
    material_name: str    
    material_model: str
    material_name_model: str
    material_unit_name: str
    material_group_name: str
    material_id: int
    order_id: str
    version: Optional[str] = None
    version_list: List[str] = None  
    route: Optional[int] = None
    cnc_route: Optional[int] = None
    production_status: Optional[str] = None
    route_list: List[OrderRouteOut] = None
    cnc_route_list: List[OrderRouteOut] = None
    class Meta:
        model = OrderParts
        fields = ['id', 'order', 'material', 'status', 'deadline', 'delivery_day', 'quantity', 'defectives', 'deliveries', 'cost', 'description', ]
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
            return f'中间件 {obj.p_orderpart.material.name}-{obj.material.name}' if obj.is_middle else obj.material.name
        return None
    @staticmethod
    def resolve_material_model(obj):
        if hasattr(obj, 'material') and obj.material:
            return obj.material.model
        return None
    @staticmethod
    def resolve_material_name_model(obj):
        if hasattr(obj, 'material') and obj.material:
            return  f"{obj.material.model} {obj.material.name}" if obj.material.model else obj.material.name
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
    def resolve_version_list(obj):
        if hasattr(obj, 'material') and obj.material:
            return [ver.version for ver in BomVersion.objects.filter(material = obj.material).order_by('-create_time')]
        return None
    
    @staticmethod
    def resolve_route_list(obj):
        if hasattr(obj, 'material') and obj.material:
            return [ver for ver in Route.objects.filter(bom_ver__material = obj.material, is_cnc=False).order_by('id')]
        return None
    
    @staticmethod
    def resolve_cnc_route_list(obj):
        if hasattr(obj, 'material') and obj.material:
            return [ver for ver in Route.objects.filter(bom_ver__material = obj.material, is_cnc=True).order_by('id')]
        return None
    
    @staticmethod
    def resolve_route(obj):
        result = ProductionPlan.objects.filter(order_part = obj).first()
        return result.route.id if result else None
    
    @staticmethod
    def resolve_cnc_route(obj):
        result = ProductionPlan.objects.filter(order_part = obj).first()
        return result.cnc_route.id if result else None
    
    @staticmethod
    def resolve_production_status(obj):
        result = ProductionPlan.objects.filter(order_part = obj).first()
        return result.status if result else "工艺工序未设定"