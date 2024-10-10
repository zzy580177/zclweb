from ninja import ModelSchema
from apps.amfui.models import *


class AlarmiIn(ModelSchema):
    

    class Meta:
        model = Alarmi
        fields = ['AllarmString', 'TypeID', 'Description_Id', ]


class AlarmiOut(ModelSchema):
    class Meta:
        model = Alarmi
        fields = ['Id', 'AllarmString', 'TypeID', 'Description_Id', ]
