from ninja import ModelSchema
from apps.fpmui.models import *


class ProcessRouteIn(ModelSchema):
    

    class Meta:
        model = ProcessRoute
        fields = ['Product_id', 'ApprovalStatus', 'Version', 'StartDay', 'Description', ]


class ProcessRouteOut(ModelSchema):
    class Meta:
        model = ProcessRoute
        fields = ['Id', 'Product_id', 'ApprovalStatus', 'Version', 'StartDay', 'Description', ]
