from ninja import ModelSchema, Schema
from apps.d_paichan.models import ProductionPlan
from typing import Optional, List
from apps.b_jihua.models import OrderParts
from apps.c_gongyi.models import Route

class ProductionPlanIn(Schema):
    order_part: int  # OrderParts.material_id
    route: Optional[int] = None  # Route ID (非CNC)
    cnc_route: Optional[int] = None  # Route ID (CNC)
    status: str = 'planned'
    description: Optional[str] = None
    order_id: str  # Order ID

class ProductionPlanOut(ModelSchema):
    class Meta:
        model = ProductionPlan
        fields = ['id', 'create_time', 'update_time', 'is_deleted', 'deleted_at', 'deleted_by', 'order_part', 'route', 'cnc_route', 'status', 'description']

class ProductionPlanUpdateIn(Schema):
    """更新生产计划的输入schema"""
    route: Optional[int] = None  # Route ID (非CNC)
    cnc_route: Optional[int] = None  # Route ID (CNC)
    status: Optional[str] = None
    description: Optional[str] = None

class ProductionPlanCreateOut(Schema):
    """创建生产计划的输出schema"""
    success: bool
    data: List[ProductionPlanOut] = []  # 成功的生产计划对象列表
    failed_items: List[str] = []  # 失败的项目信息
    message: str
