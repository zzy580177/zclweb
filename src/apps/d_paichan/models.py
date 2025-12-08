from django.db import models
from django_starter.db.base_models import *

app_name = "d_paichan"
schema = app_name

class ProductionPlan(base_model):
    """排产计划表"""
    order_part = models.OneToOneField('b_jihua.OrderParts', on_delete=models.CASCADE, verbose_name="订单零件")
    route = models.ForeignKey('c_gongyi.Route', on_delete=models.CASCADE, related_name='productionplan_route_set',limit_choices_to={'is_cnc': False}, null=True, blank=True)
    cnc_route = models.ForeignKey('c_gongyi.Route', on_delete=models.CASCADE, related_name='productionplan_cnc_route_set',  limit_choices_to={'is_cnc': True}, null=True, blank=True )
    status = models.CharField("状态", max_length=50, default="draft")
    description = models.TextField("备注", null=True, blank=True)

    def __str__(self):
        if self.route:
            return f"{self.order_part} - {self.route}"
        elif self.cnc_route:
            return f"{self.order_part} - {self.cnc_route} (CNC)"
        else:
            return f"{self.order_part} - 无工艺路线"

    class Meta:
        app_label = app_name
        db_table = f"[{schema}].[ProductionPlan]"
        verbose_name = '4.0 排产计划'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(fields=['order_part'], name='unique_order_part_productionplan')
        ]

class VProductionPlan(base_model):
    """虚拟排产计划表（视图）"""
    order_part = models.ForeignKey('b_jihua.OrderParts', on_delete=models.CASCADE, verbose_name="订单零件")
    route = models.ForeignKey('c_gongyi.Route', on_delete=models.CASCADE, verbose_name="工艺路线", null=True, blank=True)
    status = models.CharField("状态", max_length=50, default="请设定加工工艺")
    planned_quantity = models.DecimalField("计划数量", max_digits=10, decimal_places=2)
    planned_date = models.DateField("计划日期", null=True, blank=True)
    description = models.TextField("备注", null=True, blank=True)

    def __str__(self):
        return f"虚拟: {self.order_part}"

    class Meta:
        app_label = app_name
        db_table = "[d_paichan].[VProductionPlan]"
        managed = False  # 这是一个视图，不是实际表
        verbose_name = '4.0 排产计划 (虚拟)'
        verbose_name_plural = verbose_name

class ProductionOrder(base_model):
    """生产订单表"""
    order = models.ForeignKey('b_jihua.Order', on_delete=models.CASCADE, verbose_name="生产订单号")
    status = models.CharField("状态", max_length=50, default="pending")
    description = models.TextField("备注", null=True, blank=True)

    def __str__(self):
        return self.p_order

    class Meta:
        app_label = app_name
        db_table = f"[{schema}].[ProductionOrder]"
        verbose_name = '4.1 生产订单'
        verbose_name_plural = verbose_name

class WorkOrder(base_model):
    """任务工单表"""
    plan = models.ForeignKey('ProductionPlan', on_delete=models.CASCADE, verbose_name="生产订单")
    is_cnc = models.BooleanField("是否CNC", default=False)
    process = models.CharField("工序描述", max_length=50)
    sequence = models.IntegerField("工序序列")
    status = models.CharField("状态", max_length=50, default="pending")
    quantity = models.DecimalField("数量", max_digits=10, decimal_places=2)
    assigned_to = models.CharField("分配到", max_length=50, null=True, blank=True)
    start_time = models.DateTimeField("开始时间", null=True, blank=True)
    end_time = models.DateTimeField("结束时间", null=True, blank=True)
    description = models.TextField("备注", null=True, blank=True)

    def __str__(self):
        return f"{self.production_order} - {self.step} - Seq{self.sequence}"

    class Meta:
        unique_together = ('plan', 'is_cnc','sequence')    
        app_label = app_name
        db_table = f"[{schema}].[WorkOrder]"
        verbose_name = '4.2 任务工单'
        verbose_name_plural = verbose_name
