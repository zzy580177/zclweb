from ninja import ModelSchema
from apps.a_wuliao.models import *


class AttributeIn(ModelSchema):
    description: str = None
    key: str = None

    class Meta:
        model = Attribute
        fields = ['name', 'description', 'key']


class AttributeOut(ModelSchema):
    class Meta:
        model = Attribute
        fields = ['attribute_id', 'name', 'description', 'key']

class OnlyDescriptionOut(ModelSchema):
    class Meta:
        model = Attribute
        fields = ['description']