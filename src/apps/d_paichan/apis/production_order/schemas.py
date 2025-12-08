from ninja import ModelSchema
from apps.d_paichan.models import ProductionOrder

class ProductionOrderIn(ModelSchema):
    class Meta:
        model = ProductionOrder
        fields = ['id', 'order', 'status', 'description']

class ProductionOrderOut(ModelSchema):
    class Meta:
        model = ProductionOrder
        fields = ['id', 'order', 'status', 'description']
