from ninja import ModelSchema
from apps.amfui.models import *


class WorkSheetIn(ModelSchema):
    
    Cell_id: int
    
    Order_id: int
    

    class Meta:
        model = WorkSheet
        fields = ['Product_id', 'Status', 'ProcessID', 'FinishParts', 'ReqParts', 'AddReqParts', ]


class WorkSheetOut(ModelSchema):
    class Meta:
        model = WorkSheet
        fields = ['Id', 'Cell', 'Order', 'Product_id', 'Status', 'ProcessID', 'FinishParts', 'ReqParts', 'AddReqParts', ]
