from ninja import ModelSchema
from apps.pmcui.models import *
from typing import Optional
from apps.bmui.apis.material.schemas import MaterialOut


class MaterialParmIn(ModelSchema):
    
    Material_id: int
    

    class Meta:
        model = MaterialParm
        fields = ['Size', 'Stuff', 'Cost', 'Surface', 'Description', ]


class MaterialParmOut(ModelSchema):

    Material: Optional[MaterialOut]
    class Meta:
        model = MaterialParm
        fields = ['Id', 'Material', 'Size', 'Stuff', 'Cost', 'Surface', 'Description', ]
