from ninja import ModelSchema
from apps.a_wuliao.models import *


class BomIn(ModelSchema):
    

    class Meta:
        model = Bom
        fields = ['createTime', 'updateTime', 'is_deleted', 'deleted_at', 'deleted_by', 'quantity', 'level', 'remark', ]


class BomOut(ModelSchema):
    class Meta:
        model = Bom
        fields = ['createTime', 'updateTime', 'is_deleted', 'deleted_at', 'deleted_by', 'bom_id', 'version', 'p_material', 'c_material', 'quantity', 'level', 'remark', ]
