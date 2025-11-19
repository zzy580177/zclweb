from ninja import ModelSchema
from apps.c_gongyi.models import *


class CraftIn(ModelSchema):
    
    process_id: int
    
    step_id: int
    

    class Meta:
        model = Craft
        fields = ['params', ]


class CraftOut(ModelSchema):
    class Meta:
        model = Craft
        fields = ['id', 'process', 'step', 'params', ]
