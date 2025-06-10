from ninja import ModelSchema
from apps.jihuaManagerUI.models import *


class OutBoundManagIn(ModelSchema):
    

    class Meta:
        model = OutBoundManag
        fields = ['CreateTime', 'UpdateTime', 'IsDelete', 'IsActive', 'Status', 'Product_id', 'DeadLine', 'Owner', 'WH', 'Audit', 'Cost', 'LotId', 'Description', ]


class OutBoundManagOut(ModelSchema):
    class Meta:
        model = OutBoundManag
        fields = ['CreateTime', 'UpdateTime', 'IsDelete', 'IsActive', 'OrderId', 'Status', 'Product_id', 'DeadLine', 'Owner', 'WH', 'Audit', 'Cost', 'LotId', 'Description', ]
