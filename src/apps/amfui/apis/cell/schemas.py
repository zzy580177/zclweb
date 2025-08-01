from ninja import ModelSchema
from apps.amfui.models import *
from django.db.models import IntegerField


class CellIn(ModelSchema):
    

    class Meta:
        model = Cell
        fields = ['CellID', 'Plant', 'Name', 'Type', 'Stato', 'IP', 'Create', 'OnLine', 'WorkTM', ]


class CellOut(ModelSchema):
    class Meta:
        model = Cell
        fields = ['id', 'CellID', 'Plant', 'Name', 'Type', 'Stato', 'IP', 'Create', 'OnLine', 'WorkTM', ]

from pydantic import Field
from typing import Optional
from datetime import datetime

class CellDetailOut(ModelSchema):
    in_idle: int = Field(..., alias="in_idle")
    in_job: int = Field(..., alias="in_job")
    in_abnormal: int = Field(..., alias="in_abnormal") 
    in_offline: int = Field(..., alias="in_offline")
    #latest_check1: Optional[datetime] = Field(None, alias="latest_check1[0].Check1")
    class Meta:
        model = Cell
        fields = ['id', 'CellID', 'Plant', 'Name', 'Type', 'Stato', 'IP', 'Create', 'OnLine', ]

class CellIdInfoOut(ModelSchema):
    class Meta:
        model = Cell
        fields = ['id', 'CellID', 'Plant', 'Name', 'Type',]
