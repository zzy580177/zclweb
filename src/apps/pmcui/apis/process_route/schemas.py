from ninja import ModelSchema, Schema
from apps.pmcui.models import *

from ninja import Schema
from typing import List, Optional
from apps.pmcui.models import ProcessRoute
from ninja import ModelSchema
from apps.bmui.apis.material.schemas import MaterialSampleOut



class ProcessRouteIn(ModelSchema):
  

    class Meta:
        model = ProcessRoute
        fields = ['Product_id', 'ApprovalStatus', 'Version', 'StartDay', 'Parameters', 'IsCNC', 'Description', ]


class ProcessRouteOut(ModelSchema):
    Material: Optional[MaterialSampleOut]
    class Meta:
        model = ProcessRoute
        fields = ['Id', 'Product_id', 'Material',  'ApprovalStatus', 'Version', 'StartDay', 'Parameters', 'IsCNC', 'Description', ]


class ProcessRouteStepsOut(Schema):
    Material: Optional[MaterialSampleOut]
    #main_steps: List[ProcessStepSampleOut]
    class Meta:
        model = ProcessRoute
        fields = ['Id', 'Product_id', 'Material',  'ApprovalStatus', 'Version', 'IsCNC', ]

class SampleProcessRouteOut(ModelSchema):
    Material: Optional[MaterialSampleOut]
    #main_steps: List[ProcessStepSampleOut]
    SubMaterials: List[str] = []  # Assuming this is a list of strings
    class Meta:
        model = ProcessRoute
        fields = ['Id', 'Material',  'ApprovalStatus', 'Version', 'IsCNC',]

    