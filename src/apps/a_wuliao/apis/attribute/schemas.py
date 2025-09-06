from ninja import ModelSchema
from apps.a_wuliao.models import *


class AttributeIn(ModelSchema):
    

    class Meta:
        model = Attribute
        fields = ['name', 'description', ]


class AttributeOut(ModelSchema):
    class Meta:
        model = Attribute
        fields = ['attribute_id', 'name', 'description', ]

class OnlyDescriptionOut(ModelSchema):
    class Meta:
        model = Attribute
        fields = ['description']