from ninja import ModelSchema
from apps.b_jihua.models import *


class OrderPartsIn(ModelSchema):
    
    order_id: str    
    material_number: str
    material_name: str
    material_model: str
    plan_delivery: str
    quantity: str   

    class Meta:
        model = OrderParts
        fields = [ 'plan_delivery', 'quantity', 'description', ]

class OrderPartsUpdateIn(ModelSchema):
    plan_delivery: str
    quantity: str  
    defectives: str
    deliveries: str
    deadline: str
    cost: str
    order: str
    material: str

    class Meta:
        model = OrderParts
        fields = [ 'plan_delivery', 'quantity', 'status', 'deadline', 'description', ]

class OrderPartsOut(ModelSchema):
    class Meta:
        model = OrderParts
        fields = ['id', 'create_time', 'update_time', 'is_deleted', 'deleted_at', 'deleted_by', 'order', 'material', 'status', 'deadline', 'plan_delivery', 'quantity', 'defectives', 'deliveries', 'cost', 'description', ]
