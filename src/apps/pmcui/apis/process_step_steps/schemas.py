from ninja import ModelSchema
from apps.pmcui.models import *

from typing import List, Optional
from apps.pmcui.apis.process_route.schemas import ProcessRouteOut
from apps.pmcui.apis.step.schemas import StepOut
class ProcessStepStepsIn(ModelSchema):
   

    class Meta:
        model = ProcessStepSteps
        fields = ['processstep', 'step', ]


class ProcessStepStepsOut(ModelSchema):
    step: Optional[StepOut] = []
    class Meta:
        model = ProcessStepSteps
        fields = ['processstep', 'step', ]
