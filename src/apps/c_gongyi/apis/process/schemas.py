from ninja import ModelSchema
from apps.c_gongyi.models import *


class ProcessIn(ModelSchema):
    
    route_id: int
    
    subroute_id: int
    

    class Meta:
        model = Process
        fields = ['create_time', 'update_time', 'is_deleted', 'deleted_at', 'deleted_by', 'seqnum', 'params', 'description', ]


class ProcessOut(ModelSchema):
    class Meta:
        model = Process
        fields = ['id', 'create_time', 'update_time', 'is_deleted', 'deleted_at', 'deleted_by', 'route', 'subroute', 'seqnum', 'params', 'description', ]
