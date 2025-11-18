from ninja import ModelSchema
from apps.b_jihua.models import *
from typing import Optional

class OrderIn(ModelSchema):
    order_id: str 
    plan_delivery: str  

    class Meta:
        model = Order
        fields = [  'product_id',  'plan_delivery',  'lot_id', 'description', ]

class OrderUpdataIn(ModelSchema):
    plan_delivery: str
    deadline: Optional[str] = None

    class Meta:
        model = Order
        fields = [  'product_id',  'plan_delivery','deadline', 'lot_id', 'description', 'status' ] 

class OrderOut(ModelSchema):
    class Meta:
        model = Order
        fields = ['create_time', 'update_time', 'is_deleted', 'deleted_at', 'deleted_by', 'order_id', 'status', 'product_id', 'deadline', 'plan_delivery', 'owner', 'wh', 'audit', 'cost', 'lot_id', 'description', ]
