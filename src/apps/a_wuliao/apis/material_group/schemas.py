from ninja import ModelSchema
from apps.a_wuliao.models import *
from datetime import datetime
from typing import Optional, List

class MaterialGroupIn(ModelSchema):
    sub_group: Optional[str] = None
    min_group: Optional[str] = None
    group: Optional[str] = None
    parent: Optional[str] = None  # 输入时可以是字符串（number），API内部会转换为MaterialGroup实例
    level: Optional[str] = None
    
    class Meta:
        model = MaterialGroup
        fields = [ 'group_id', 'name', 'number', ]


class MaterialGroupOut(ModelSchema):

    class Meta:
        model = MaterialGroup
        fields = ['createTime', 'updateTime', 'is_deleted', 'deleted_at', 'deleted_by', 'group_id', 'name', 'parent', 'number', 'level', 'group', 'sub_group', 'min_group', ]
