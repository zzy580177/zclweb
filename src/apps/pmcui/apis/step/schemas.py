from ninja import ModelSchema
from apps.pmcui.models import *


class StepIn(ModelSchema):
    
    EqpType_id: int  # Specify the type, e.g., int. Add '= None' if optional.
    

    class Meta:
        model = Step
        fields = ['Name', 'UCost', 'HCost', 'Description', ]


class StepOut(ModelSchema):
    class Meta:
        model = Step
        fields = ['Id', 'Name', 'EqpType', 'UCost', 'HCost', 'Description', ]
