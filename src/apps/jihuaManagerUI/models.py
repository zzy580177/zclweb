from django.db import models
from django_starter.db.models import POrder

app_name = "jihuaManagerUI"  # 关联应用名称
schema = app_name

# Create your models here.
class POrder(POrder):
    """订单表"""
    class Meta:
        db_table = f"[{schema}].[POrder]"
        app_label = app_name
        verbose_name = '产品订单管理'
        verbose_name_plural = verbose_name

class OutBoundManag(POrder):
	class Meta:
		proxy = True
		app_label = app_name
		verbose_name = '订单外发管理'
		verbose_name_plural = verbose_name