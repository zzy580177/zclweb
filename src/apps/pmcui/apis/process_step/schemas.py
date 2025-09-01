
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

class ProcessStepOut(ModelSchema):
    class Meta:
        model = ProcessStep
        fields = ['PFId', 'Steps', 'Route', 'subRoute', 'Parameters', 'SeqNum', 'Description']

class ProcessStepSampleIn(ModelSchema):    
    Steps_Step_Id: List[str] = None    
    Steps_Step_Name: List[str] = None    
    Process_Steps_Parm: List[str] = None    
    Steps_Step_EqpType_Name: Optional[str] = None
    #Route_id: Optional[int] = None
    FNumber: Optional[str] = None 
    FModel: Optional[str] = None
    FName: Optional[str] = None
    FId: Optional[int] = None
    POrder_id: Optional[str] = None
    class Meta:
        model = ProcessStep
        fields = ['SeqNum', 'Description']
    
class ProcessStepSampleOut(ModelSchema):
    Steps_Step_Id: List[str] = None    
    Steps_Step_Name: List[str] = None    
    Steps_Step_EqpType_Name: Optional[str] = None
    Process_Steps_Parm: List[str] = None    
    Route_id: Optional[int] = None
    FNumber: Optional[str] = None 
    FModel: Optional[str] = None
    FName: Optional[str] = None
    FId: Optional[int] = None
    POrder_id: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    class Meta:
        model = ProcessStep
        fields = ['SeqNum', 'Description']

    @staticmethod
    def resolve_Steps_Step_Id(obj):
        steps = []
        for step in obj.processstepsteps_set.select_related('step').all():
            step_out = StepOut.from_orm(step.step)
            steps.append(step_out.Id)
        return steps

    @staticmethod
    def resolve_Steps_Step_Name(obj):
        steps = []
        for step in obj.processstepsteps_set.select_related('step').all():
            step_out = StepOut.from_orm(step.step)
            steps.append(step_out.Name)
        return steps

    @staticmethod
    def resolve_Process_Steps_Parm(obj):
        Parms = []
        for step in obj.processstepsteps_set.select_related('step').all():
            Parms.append(step.parameters)
        return Parms
    
    @staticmethod
    def resolve_Steps_Step_EqpType_Name(obj):
        for step in obj.processstepsteps_set.select_related('step').all():
            step_out = StepOut.from_orm(step.step)
            return step_out.EqpType.Name

    @staticmethod
    def resolve_Route_Material_FNumber(obj):
        if not obj.Route:
            return None
        if not obj.Route.Material:
            return None
        return obj.Route.Material.FNumber

    @staticmethod
    def resolve_Route_Material_FModel(obj):
        if not obj.Route:
            return None
        if not obj.Route.FModel:
            return None
        return obj.Route.Material.FModel

class ProcessStepRouteOut(Schema):
    route_id: int
    process_steps: List[ProcessStepSampleIn]
    class Config:
        arbitrary_types_allowed = True