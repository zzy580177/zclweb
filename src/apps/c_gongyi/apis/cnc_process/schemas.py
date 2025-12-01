from ninja import ModelSchema
from apps.c_gongyi.models import *


class CNCProcessIn(ModelSchema):
    
    route_id: int
    

    class Meta:
        model = CNCProcess
        fields = ['create_time', 'update_time', 'is_deleted', 'deleted_at', 'deleted_by', 'seqnum', 'params', 'description', ]


class CNCProcessOut(ModelSchema):
    class Meta:
        model = CNCProcess
        fields = ['id', 'create_time', 'update_time', 'is_deleted', 'deleted_at', 'deleted_by', 'route', 'seqnum', 'params', 'description', ]
