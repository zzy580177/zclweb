from ninja import ModelSchema
from apps.pmcui.models import *
from apps.bmui.apis.attribute.schemas import AttributeOut
from typing import Optional


class StepIn(ModelSchema):
    
    EqpType_id: int  # Specify the type, e.g., int. Add '= None' if optional.
    

    class Meta:
        model = Step
        fields = ['Name', 'UCost', 'HCost', 'Description', ]


class StepOut(ModelSchema):
    EqpType:Optional[AttributeOut]
    class Meta:
        model = Step
        fields = ['Id', 'Name', 'EqpType','UCost', 'HCost', 'Description']

class StepSampleOut(ModelSchema):
    EqpName:Optional[str]
    class Meta:
        model = Step
        fields = ['Id', 'Name', 'UCost', 'HCost', 'Description']

