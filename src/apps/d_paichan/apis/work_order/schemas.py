from ninja import ModelSchema
from apps.d_paichan.models import WorkOrder

class WorkOrderIn(ModelSchema):
    class Meta:
        model = WorkOrder
        fields = ['production_order', 'step', 'sequence', 'status', 'quantity', 'assigned_to', 'start_time', 'end_time', 'description']

class WorkOrderOut(ModelSchema):
    class Meta:
        model = WorkOrder
        fields = ['id', 'create_time', 'update_time', 'is_deleted', 'deleted_at', 'deleted_by', 'production_order', 'step', 'sequence', 'status', 'quantity', 'assigned_to', 'start_time', 'end_time', 'description']
