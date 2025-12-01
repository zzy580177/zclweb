from ninja import ModelSchema
from apps.c_gongyi.models import *
from typing import Optional


class StepIn(ModelSchema):    
    type_name: str
    ucost: Optional[str] = None
    hcost: Optional[str] = None
    

    class Meta:
        model = Step
        fields = [ 'name', 'ucost', 'hcost', 'description', ]


class StepOut(ModelSchema):
    class Meta:
        model = Step
        fields = ['id', 'create_time', 'update_time', 'is_deleted', 'deleted_at', 'deleted_by', 'name', 'type', 'ucost', 'hcost', 'description', ]
