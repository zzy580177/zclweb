from ninja import ModelSchema
from apps.d_paichan.models import WorkOrder

class WorkOrderIn(ModelSchema):
    class Meta:
        model = WorkOrder
        fields = ['plan', 'process', 'sequence', 'status', 'quantity', 'assigned_to', 'start_time', 'end_time', 'description']

class WorkOrderOut(ModelSchema):
    class Meta:
        model = WorkOrder
        fields = ['id',  'plan', 'is_cnc', 'process', 'sequence', 'status', 'quantity', 'assigned_to', 'start_time', 'end_time', 'description']
