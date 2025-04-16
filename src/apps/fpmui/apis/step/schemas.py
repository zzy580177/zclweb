from ninja import ModelSchema
from apps.fpmui.models import *


class StepIn(ModelSchema):
    

    class Meta:
        model = Step
        fields = ['Name', 'EqpType', 'Description', ]


class StepOut(ModelSchema):
    class Meta:
        model = Step
        fields = ['Id', 'Name', 'EqpType', 'Description', ]
