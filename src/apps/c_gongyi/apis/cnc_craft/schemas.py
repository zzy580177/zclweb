from ninja import ModelSchema
from apps.c_gongyi.models import *


class CNCCraftIn(ModelSchema):
    
    process_id: int
    
    step_id: int
    

    class Meta:
        model = CNCCraft
        fields = ['step_num', 'params', ]


class CNCCraftOut(ModelSchema):
    class Meta:
        model = CNCCraft
        fields = ['id', 'process', 'step_num', 'step', 'params', ]
