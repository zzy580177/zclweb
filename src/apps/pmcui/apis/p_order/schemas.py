from ninja import ModelSchema
from apps.pmcui.models import *


class POrderIn(ModelSchema):
    

    class Meta:
        model = POrder
        fields = ['CreateTime', 'UpdateTime', 'IsDelete', 'IsActive', 'Status', 'Product_id', 'DeadLine', 'Owner', 'WH', 'Audit', 'Cost', 'LotId', 'Description', ]


class POrderOut(ModelSchema):
    class Meta:
        model = POrder
        fields = ['CreateTime', 'UpdateTime', 'IsDelete', 'IsActive', 'OrderId', 'Status', 'Product_id', 'DeadLine', 'Owner', 'WH', 'Audit', 'Cost', 'LotId', 'Description', ]
