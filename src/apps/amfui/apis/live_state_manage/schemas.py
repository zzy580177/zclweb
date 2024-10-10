from ninja import ModelSchema
from apps.amfui.models import *


class LiveStateManageIn(ModelSchema):
    
    Cell_id: int
    
    WorkSheet_id: str
    

    class Meta:
        model = LiveStateManage
        fields = ['Check1', 'Check2', 'OnLine', ]


class LiveStateManageOut(ModelSchema):
    class Meta:
        model = LiveStateManage
        fields = ['id', 'Cell', 'Check1', 'Check2', 'WorkSheet', 'OnLine', ]
