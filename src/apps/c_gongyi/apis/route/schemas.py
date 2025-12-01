from ninja import ModelSchema
from django.db.models import Q
from apps.c_gongyi.models import *
from typing import List
from apps.c_gongyi.apis.process.schemas import ProcessOut
from apps.a_wuliao.apis.bom_version.schemas import BomVersionOut
from apps.a_wuliao.models import Bom, Material
from pydantic import Field


class RouteIn(ModelSchema):
    
    bom_ver_id: int
    

    class Meta:
        model = Route
        fields = ['create_time', 'update_time', 'is_deleted', 'deleted_at', 'deleted_by', 'is_cnc', 'product_id', 'approval_status', 'params', 'description', ]


class RouteOut(ModelSchema):
    text: str = Field(default_factory=str)
    #processes: List[ProcessOut] = Field(default_factory=list)
    #subparts: List[BomVersionOut] = Field(default_factory=list)
    #@staticmethod
    def resolve_processes(obj: Route) -> List[ProcessOut]:
        processes = Process.objects.filter(Q(route=obj) | Q(subroute=obj)).order_by('seqnum').prefetch_related('steps')
        return processes
    @staticmethod
    def resolve_text(obj: Route) -> str:
        return f"工艺{obj.bom_ver}-V{obj.route_ver}"
    #@staticmethod
    def resolve_subparts(obj: Route) -> List[BomVersionOut]:
        bom_ver = obj.bom_ver
        if bom_ver:
            qs = Bom.objects.filter(version__version=bom_ver.version, p_material=bom_ver.material).values_list('version', flat=True)
            qs = BomVersion.objects.filter(id__in=qs).order_by('id')
            return qs
        return []
    class Meta: 
        model = Route
        fields = ['id', 'bom_ver', 'is_cnc', 'product_id', 'approval_status', 'params', 'description']
