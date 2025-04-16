from ninja import ModelSchema
from apps.fpmui.models import *


class ProcessStepIn(ModelSchema):
    
    Step_id: int
    
    Route_id: int
    

    class Meta:
        model = ProcessStep
        fields = ['Parameters', 'SeqNum', 'Description', ]


class ProcessStepOut(ModelSchema):
    class Meta:
        model = ProcessStep
        fields = ['StepId', 'Step', 'Route', 'Parameters', 'SeqNum', 'Description', ]
