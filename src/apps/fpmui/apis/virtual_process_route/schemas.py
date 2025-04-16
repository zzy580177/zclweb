from ninja import ModelSchema
from apps.fpmui.models import *


class VirtualProcessRouteIn(ModelSchema):
    

    class Meta:
        model = VirtualProcessRoute
        fields = ['Product_id', 'ApprovalStatus', 'Version', 'StartDay', 'Description', ]


class VirtualProcessRouteOut(ModelSchema):
    class Meta:
        model = VirtualProcessRoute
        fields = ['Id', 'Product_id', 'ApprovalStatus', 'Version', 'StartDay', 'Description', ]
