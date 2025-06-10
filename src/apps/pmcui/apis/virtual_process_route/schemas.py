from ninja import ModelSchema
from apps.pmcui.models import *


class VirtualProcessRouteIn(ModelSchema):
    

    class Meta:
        model = VirtualProcessRoute
        fields = ['Product_id', 'ApprovalStatus', 'Version', 'StartDay', 'Parameters', 'IsCNC', 'Description', ]


class VirtualProcessRouteOut(ModelSchema):
    class Meta:
        model = VirtualProcessRoute
        fields = ['Id', 'Product_id', 'ApprovalStatus', 'Version', 'StartDay', 'Parameters', 'IsCNC', 'Description', ]
