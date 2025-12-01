from ninja import ModelSchema, Schema
from apps.c_gongyi.models import *
from typing import List, Optional


class CNCProcessIn(ModelSchema):

    route_id: int


    class Meta:
        model = CNCProcess
        fields = ['create_time', 'update_time', 'is_deleted', 'deleted_at', 'deleted_by', 'seqnum', 'params', 'description', ]


class CNCProcessOut(ModelSchema):
    steps_step_ids: Optional[List[str]] = None
    steps_step_names: Optional[List[str]] = None
    steps_parms: Optional[List[dict]] = None

    class Meta:
        model = CNCProcess
        fields = ['id', 'create_time', 'update_time', 'is_deleted', 'deleted_at', 'deleted_by', 'route', 'seqnum', 'params', 'description', ]

    @staticmethod
    def resolve_steps_step_ids(obj: CNCProcess) -> List[int]:
        crafts = CNCCraft.objects.filter(process=obj).order_by('step_num')
        return [str(craft.step.id) for craft in crafts]

    @staticmethod
    def resolve_steps_step_names(obj: CNCProcess) -> List[str]:
        crafts = CNCCraft.objects.filter(process=obj).order_by('step_num')
        return [craft.step.name for craft in crafts]

    @staticmethod
    def resolve_steps_parms(obj: CNCProcess) -> List[dict]:
        crafts = CNCCraft.objects.filter(process=obj).order_by('step_num')
        return [craft.params if craft.params else {} for craft in crafts]


class CNCRouteCreateIn(Schema):
    """创建CNC工艺路线的输入schema"""
    material_id: int
    version: str
    order_id: str
    product_id: Optional[str] = None

    # CNC工序列表
    cnc_processes: List[dict] = []  # 每个dict包含：seqnum, steps_step_ids, steps_parms, params, description


class CNCRouteCreateOut(Schema):
    """创建CNC工艺路线的输出schema"""
    route_id: int
    route_text: str
    message: str
