from ninja import ModelSchema
from apps.d_paichan.models import ProductionPlan
from typing import Optional

class ProductionPlanIn(ModelSchema):
    class Meta:
        model = ProductionPlan
        fields = ['order_part', 'route', 'status', 'planned_quantity', 'planned_date', 'description']

class ProductionPlanOut(ModelSchema):
    class Meta:
        model = ProductionPlan
        fields = ['id', 'create_time', 'update_time', 'is_deleted', 'deleted_at', 'deleted_by', 'order_part', 'route', 'status', 'planned_quantity', 'planned_date', 'description']
