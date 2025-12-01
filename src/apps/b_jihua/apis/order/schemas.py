from ninja import ModelSchema
from apps.b_jihua.models import *
from typing import Optional

class OrderIn(ModelSchema):
    order_id: Optional[str] = None
    status: Optional[str] = None
    delivery_day: Optional[str] = None
    deadline: Optional[str] = None
    product_id: Optional[str] = None
    owner: Optional[str] = None
    wh: Optional[str] = None
    audit: Optional[str] = None
    cost: Optional[str] = None
    lot_id: Optional[str] = None
    description: Optional[str] = None

    class Meta:
        model = Order
        fields = ['order_id', 'status', 'product_id', 'deadline', 'delivery_day', 'owner', 'wh', 'audit', 'cost', 'lot_id', 'description', ]

class OrderOut(ModelSchema):
    class Meta:
        model = Order
        fields = ['create_time', 'update_time', 'is_deleted', 'deleted_at', 'deleted_by', 'order_id', 'status', 'product_id', 'deadline', 'delivery_day', 'owner', 'wh', 'audit', 'cost', 'lot_id', 'description', ]
