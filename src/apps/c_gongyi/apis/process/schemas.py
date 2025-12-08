from ninja import ModelSchema, Schema
from apps.c_gongyi.models import *
from typing import List, Optional
import json



class ProcessIn(ModelSchema):
    
    steps_step_ids: Optional[List[str]]=None
    steps_step_names: Optional[List[str]]=None
    steps_parms: Optional[List[str]]=None
    type_name: Optional[str] = None
    isCNC: Optional[bool] = None

    material_id: Optional[int] = None
    material_name: Optional[str] = None
    material_number: Optional[str] = None
    material_model: Optional[str] = None 
    version: Optional[str] = None

    order_id: Optional[str] = None
    seqnum: str    
    params: Optional[dict]=None

    class Meta:
        model = Process
        fields = [ 'seqnum', 'params', 'description', ]

from ninja import ModelSchema
from apps.c_gongyi.models import *
from typing import List, Optional

class ProcessOut(ModelSchema):
    steps_step_ids: Optional[List[str]] = None
    steps_step_names: Optional[List[str]] = None
    steps_step_nums: Optional[List[int]] = None
    steps_parms: Optional[List[str]] = None
    type_name: Optional[str] = None

    class Meta:
        model = Process
        prefetch_related = ['steps', 'craft_set']
        fields = ['route', 'subroute', 'steps', 'seqnum', 'params', 'description', ]
    
    @staticmethod
    def resolve_steps_step_ids(obj: Process) -> List[int]:
        result = [str(step.id) for step in obj.steps.all().order_by('pk')]
        return result
    
    @staticmethod
    def resolve_steps_step_nums(obj: Process) -> List[str]:
        crafts = Craft.objects.filter(process=obj).order_by('pk')
        result = []
        for craft in crafts:
            if craft.step_num:
                result.append(craft.step_num)
        return result

    @staticmethod
    def resolve_steps_step_names(obj: Process) -> List[str]:
        return [step.name for step in obj.steps.all().order_by('pk')]

    @staticmethod
    def resolve_steps_parms(obj: Process) -> List[str]:
        crafts = Craft.objects.filter(process=obj).order_by('pk')
        result = []
        for craft in crafts:
            if craft.params:
                params_json = json.dumps(craft.params, ensure_ascii=False)
                result.append(params_json)
            else:
                result.append('')
        return result

    @staticmethod
    def resolve_type_name(obj: Process) -> Optional[str]:
        type_names = set(step.type.name for step in obj.steps.all() if step.type.name)
        return ', '.join(type_names) if type_names else None


class RouteCreateIn(Schema):
    """创建CNC工艺路线的输入schema"""
    material_id: int
    version: str
    order_id: str
    product_id: Optional[str] = None
    is_cnc: bool = False
    # 工序列表
    processes: List[dict] = []  # 每个dict包含：seqnum, steps_step_ids, steps_parms, params, description


class RouteCreateOut(Schema):
    """创建CNC工艺路线的输出schema"""
    success: bool
    data: Optional[dict] = None
    message: str