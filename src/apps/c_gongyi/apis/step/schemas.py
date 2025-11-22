from ninja import ModelSchema
from apps.c_gongyi.models import *


class StepIn(ModelSchema):
    
    type_id: str
    

    class Meta:
        model = Step
        fields = ['create_time', 'update_time', 'is_deleted', 'deleted_at', 'deleted_by', 'name', 'ucost', 'hcost', 'description', ]


class StepOut(ModelSchema):
    class Meta:
        model = Step
        fields = ['id', 'create_time', 'update_time', 'is_deleted', 'deleted_at', 'deleted_by', 'name', 'type', 'ucost', 'hcost', 'description', ]
