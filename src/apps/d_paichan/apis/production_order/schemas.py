from ninja import ModelSchema
from apps.d_paichan.models import ProductionOrder

class ProductionOrderIn(ModelSchema):
    class Meta:
        model = ProductionOrder
        fields = ['plan', 'order_number', 'status', 'quantity', 'start_date', 'end_date', 'description']

class ProductionOrderOut(ModelSchema):
    class Meta:
        model = ProductionOrder
        fields = ['id', 'create_time', 'update_time', 'is_deleted', 'deleted_at', 'deleted_by', 'plan', 'order_number', 'status', 'quantity', 'start_date', 'end_date', 'description']
