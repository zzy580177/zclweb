from ninja import ModelSchema, Schema
from apps.pmcui.models import *

from ninja import Schema
from typing import List, Optional
from apps.pmcui.apis.process_step.schemas import ProcessStepOut
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


class ProcessRouteStepsOut(Schema):
    Id: int
    Product_id: str
    Material: Optional[MaterialOut]
    ApprovalStatus: str
    Version: Optional[int]
    StartDay: Optional[str]
    Parameters: Optional[dict]
    IsCNC: Optional[bool]
    Description: Optional[str]
    main_steps: List[ProcessStepOut]