from ninja import ModelSchema
from apps.c_gongyi.models import *


class VirtualProcessRouteIn(ModelSchema):
    
    bom_ver_id: int
    

    class Meta:
        model = VirtualProcessRoute
        fields = ['create_time', 'update_time', 'is_deleted', 'deleted_at', 'deleted_by', 'is_cnc', 'product_id', 'approval_status', 'params', 'description', ]


class VirtualProcessRouteOut(ModelSchema):
    class Meta:
        model = VirtualProcessRoute
        fields = ['id', 'create_time', 'update_time', 'is_deleted', 'deleted_at', 'deleted_by', 'bom_ver', 'is_cnc', 'product_id', 'approval_status', 'params', 'description', ]
