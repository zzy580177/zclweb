from ninja import ModelSchema
from apps.amfui.models import *


class PezziIn(ModelSchema):
    
    Cell_id: int
    
    WorkSheet_id: str
    

    class Meta:
        model = Pezzi
        fields = ['DataTime', 'Pezzi', 'ReqPezzi', 'ResidPezzi', 'PieceTime', ]


class PezziOut(ModelSchema):
    class Meta:
        model = Pezzi
        fields = ['id', 'Cell', 'WorkSheet', 'DataTime', 'Pezzi', 'ReqPezzi', 'ResidPezzi', 'PieceTime', ]
