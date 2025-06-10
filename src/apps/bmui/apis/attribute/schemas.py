from ninja import ModelSchema
from apps.bmui.models import *


class AttributeIn(ModelSchema):
    

    class Meta:
        model = Attribute
        fields = ['Name', 'Description', ]


class AttributeOut(ModelSchema):
    class Meta:
        model = Attribute
        fields = ['Id', 'Name', 'Description', ]
