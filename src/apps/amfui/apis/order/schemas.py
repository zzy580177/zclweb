from ninja import ModelSchema
from apps.amfui.models import *


class OrderIn(ModelSchema):
    

    class Meta:
        model = Order
        fields = ['Id', 'Status', 'Colour', 'Product_id', 'ReqParts', ]


class OrderOut(ModelSchema):
    class Meta:
        model = Order
        fields = ['id', 'Id', 'Status', 'Colour', 'Product_id', 'ReqParts', ]
