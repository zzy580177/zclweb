from ninja import ModelSchema, Schema
from apps.pmcui.models import *

from typing import List, Optional
from apps.pmcui.apis.step.schemas import StepOut
class ProcessStepIn(ModelSchema):
    
    Step_id: str
    
    Route_id: int
    
    subRoute_id: int
    

    class Meta:
        model = ProcessStep
        fields = ['Parameters', 'SeqNum', 'Description', ]

class StepWithParamOut(Schema):
    id: int
    processstep_id: int
    step_id: str  # Changed to string to match actual FNumber values
    parameters: Optional[str] = None
    step: StepOut

class ProcessStepOut(ModelSchema):
    Steps: List[StepWithParamOut] = []  # Note: This matches the model's many-to-many field name

    class Meta:
        model = ProcessStep
        fields = ['PFId', 'Steps', 'Route', 'subRoute', 'Parameters', 'SeqNum', 'Description']

    @staticmethod
    def resolve_Steps(obj):
        steps_with_params = []
        for step in obj.processstepsteps_set.select_related('step').all():
            step_out = StepOut.from_orm(step.step)
            steps_with_params.append(StepWithParamOut(
                id=step.id,
                processstep_id=step.processstep_id,
                step_id=step.step_id,
                parameters=step.parameters,
                step=step_out
            ))
        return steps_with_params
