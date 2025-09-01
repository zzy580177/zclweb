from ninja import ModelSchema, Schema
from apps.pmcui.models import *

from typing import List, Optional
from apps.pmcui.apis.process_route.schemas import ProcessRouteOut
from apps.pmcui.apis.step.schemas import StepOut
from apps.pmcui.apis.process_step.schemas import ProcessStepOut
class ProcessStepStepsIn(ModelSchema):
   

    class Meta:
        model = ProcessStepSteps
        fields = ['processstep', 'step', ]

class ProcessStepStepsOut(ModelSchema):
    step: Optional[StepOut] = None
    processstep: Optional[ProcessStepOut] = None
    class Meta:
        model = ProcessStepSteps
        fields = ['id','processstep', 'step', 'parameters']

class RouteSubMaterialOut(Schema):
    FId: int
    FNumber: str
    FName: str
    FModel: str
