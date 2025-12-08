from ninja import ModelSchema
from apps.a_wuliao.models import *
from typing import Optional, List
from apps.b_jihua.apis.order_parts.schemas import OrderRouteOut
from apps.c_gongyi.models import Route

class MaterialIn(ModelSchema): 
    unit: str  
    p_material: Optional[str] = None

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

class MaterilRoutesOut(ModelSchema):
    material_name: Optional[str] = None
    material_number: Optional[str] = None
    material_model: Optional[str] = None   
    route_list: List[OrderRouteOut] = None
    cnc_route_list: List[OrderRouteOut] = None
    route: Optional[int] = None
    cnc_route: Optional[int] = None
    class Meta:
        model = Material
        fields =  ['material_id']
    
    @staticmethod
    def resolve_routeList(obj):
        result = {'cnc_route':[], 'route':[]}
        route_qs =Route.objects.filter(bom_ver__material = obj).order_by('id')
        result['cnc_route'] = [route.route_id for route in route_qs if route.is_cnc]
        result['route'] = [route.route_id for route in route_qs if not route.is_cnc]
        return result
    
    @staticmethod
    def resolve_route_list(obj):
        # 优先使用从ProductionPlan获取的route
        if hasattr(obj, '_production_plan_route') and obj._production_plan_route:
            # 返回ProductionPlan中指定的route
            route = Route.objects.filter(id=obj._production_plan_route, is_cnc=False).first()
            return [route] if route else []
        # 否则返回所有可用的route
        return [ver for ver in Route.objects.filter(bom_ver__material = obj, is_cnc=False).order_by('id')]
    
    @staticmethod
    def resolve_cnc_route_list(obj):
        # 优先使用从ProductionPlan获取的cnc_route
        if hasattr(obj, '_production_plan_cnc_route') and obj._production_plan_cnc_route:
            # 返回ProductionPlan中指定的cnc_route
            route = Route.objects.filter(id=obj._production_plan_cnc_route, is_cnc=True).first()
            return [route] if route else []
        # 否则返回所有可用的cnc_route
        return [ver for ver in Route.objects.filter(bom_ver__material = obj, is_cnc=True).order_by('id')]
    
    @staticmethod
    def resolve_route(obj):
        # 返回ProductionPlan中的route ID
        if hasattr(obj, '_production_plan_route'):
            return obj._production_plan_route
        return None
    
    @staticmethod
    def resolve_cnc_route(obj):
        # 返回ProductionPlan中的cnc_route ID
        if hasattr(obj, '_production_plan_cnc_route'):
            return obj._production_plan_cnc_route
        return None
    
    @staticmethod
    def resolve_material_name(obj):
        return obj.name
    
    @staticmethod
    def resolve_material_number(obj):
        return getattr(obj, 'number', None)
    
    @staticmethod
    def resolve_material_model(obj):
        return getattr(obj, 'model', None)
