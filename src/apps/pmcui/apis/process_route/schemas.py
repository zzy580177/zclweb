from ninja import ModelSchema
from apps.pmcui.models import *

from typing import Optional
from apps.bmui.apis.material.schemas import MaterialOut

class ProcessRouteIn(ModelSchema):
    

    class Meta:
        model = ProcessRoute
        fields = ['Product_id', 'ApprovalStatus', 'Version', 'StartDay', 'Parameters', 'IsCNC', 'Description', ]


class ProcessRouteOut(ModelSchema):
    Material: Optional[MaterialOut]
    class Meta:
        model = ProcessRoute
        fields = ['Id', 'Product_id', 'Material',  'ApprovalStatus', 'Version', 'StartDay', 'Parameters', 'IsCNC', 'Description', ]
