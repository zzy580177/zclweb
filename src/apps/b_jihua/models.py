from django.db import models
from django_starter.db.base_models import *
# Create your models here.

app_name = "b_jihua"  # 应用名称
schema = app_name

class Order(base_model):
    """订单表"""
    order_id = models.CharField("订单号",max_length =50, primary_key=True); 
    status = models.CharField("订单状态",max_length=50, null=True, blank=True);
    product_id = models.CharField("产品编号",max_length=50, null=True, blank=True);
    deadline = models.DateField("交货日期",null=True, blank=True);
    plan_delivery = models.DateField("计划交付日期",null=True, blank=True);
    owner = models.CharField("制单员",max_length=50, null=True, blank=True);
    wh = models.CharField("仓库员",max_length=50, null=True, blank=True);
    audit = models.CharField("审计员",max_length=50, null=True, blank=True);
    cost = models.DecimalField("成本", max_digits=10, decimal_places=2, null=True, blank=True)
    lot_id = models.CharField("批次号", max_length=50, null=True, blank=True);
    description = models.TextField("备注", null=True, blank=True); 

    def __str__(self):
        return self.order_id
    class Meta:
        app_label = app_name
        db_table = f"[{schema}].[Order]"
        verbose_name = '2.0 生产订单'
        verbose_name_plural = verbose_name
        ordering = ['deadline', 'status']

class OrderParts(base_model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, verbose_name="订单号");
    material = models.ForeignKey('a_wuliao.Material', on_delete=models.CASCADE, verbose_name="物料编号");
    status = models.CharField("状态",max_length=50, null=True, blank=True);
    deadline = models.DateField("交货日期",null=True, blank=True);
    plan_delivery = models.DateField("计划交付日期",null=True, blank=True);
    quantity = models.DecimalField("数量", max_digits=10, decimal_places=2);
    defectives = models.DecimalField("不良品数量", max_digits=10, decimal_places=2, default=0);
    deliveries = models.DecimalField("交付数量", max_digits=10, decimal_places=2, default=0);
    cost = models.DecimalField("成本", max_digits=10, decimal_places=2, null=True, blank=True);
    description = models.TextField("备注", null=True, blank=True);

    def __str__(self):
        order_str = str(self.order) if self.order is not None else ''
        material_str = str(self.material) if self.material is not None else ''
        return f"{order_str} {material_str}".strip()
    class Meta:
        unique_together = ('order', 'material')
        app_label = app_name
        db_table = f"[{schema}].[OrderParts]"
        verbose_name = '2.1 订单详情'
        verbose_name_plural = verbose_name
        ordering = ['deadline', 'status']
