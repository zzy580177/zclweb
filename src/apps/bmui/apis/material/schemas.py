from ninja import ModelSchema
from apps.bmui.models import *


class MaterialIn(ModelSchema):
    

    class Meta:
        model = Material
        fields = ['Name', 'Type', 'Source', 'Description', ]


class MaterialOut(ModelSchema):
    class Meta:
        model = Material
        fields = ['Id', 'Name', 'Type', 'Source', 'Description', ]
