from ninja import ModelSchema
from apps.amfui.models import *


class OrderIn(ModelSchema):
    

    class Meta:
        model = Order
        fields = ['Status', 'Colour', 'Product_id', 'ReqParts', 'DeadLine', 'Progress', ]


class OrderOut(ModelSchema):
    class Meta:
        model = Order
        fields = ['OrderId', 'Status', 'Colour', 'Product_id', 'ReqParts', 'DeadLine', 'Progress', ]
