from ninja import ModelSchema
from apps.pmcui.models import *

from typing import List, Optional
from apps.pmcui.apis.process_route.schemas import ProcessRouteOut
from apps.pmcui.apis.step.schemas import StepOut
class ProcessStepIn(ModelSchema):
    
    Step_id: str
    
    Route_id: int
    
    subRoute_id: int
    

    class Meta:
        model = ProcessStep
        fields = ['Parameters', 'SeqNum', 'Description', ]


class ProcessStepOut(ModelSchema):
    Route: Optional[ProcessRouteOut]
    subRoute: Optional[ProcessRouteOut]
    Steps: List[StepOut] = []
    class Meta:
        model = ProcessStep
        fields = ['PFId', 'Steps', 'Route', 'subRoute', 'Parameters', 'SeqNum', 'Description', ]
