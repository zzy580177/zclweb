from ninja import ModelSchema
from apps.c_gongyi.models import *
from typing import List, Optional


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
    def resolve_steps_step_names(obj: Process) -> List[str]:
        return [step.name for step in obj.steps.all().order_by('pk')]

    @staticmethod
    def resolve_steps_parms(obj: Process) -> List[str]:
        crafts = Craft.objects.filter(process=obj).order_by('pk')
        return [str(craft.params) if craft.params else '' for craft in crafts]


    @staticmethod
    def resolve_type_name(obj: Process) -> Optional[str]:
        type_names = set(step.type.name for step in obj.steps.all() if step.type.name)
        return ', '.join(type_names) if type_names else None
