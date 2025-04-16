from django.db import models
from django.conf import settings
#from django_starter.db.models import BOM, Material, BOMLevel

# Create your models here.
schema = settings.DATABASES["default"].get("SCHEMA", "default_schema")
app_name = 'bmui'
class Material(models.Model):
    """物料表"""
    Id = models.AutoField("物料编号", primary_key=True)
    Name = models.CharField("物料名称", max_length=100)   
    Type = models.CharField("物料型号", max_length=100)     
    Source = models.CharField("获取来源", max_length=100)
    Attribute  = models.TextField("辅助属性", null=True, blank=True)
    Description = models.TextField("备注", null=True, blank=True)

    def __str__(self):
        return self.Name

    class Meta:
        app_label = app_name
        db_table = "[%s].[Material]" % schema
        verbose_name = '物料'
        verbose_name_plural = verbose_name


class BOM(models.Model):
    """物料清单表"""
    Id = models.AutoField("BOM编号", primary_key=True)
    Material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name="物料")
    Quantity = models.IntegerField("数量")
    ParentBOM = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_boms', verbose_name="父级BOM")

    def __str__(self):
        return f"BOM {self.Id} - {self.Material.Name}"

    class Meta:
        app_label = app_name
        db_table = "[%s].[BOM]" % schema
        verbose_name = '物料清单'
        verbose_name_plural = verbose_name


class BOMLevel(models.Model):
    """BOM层级表"""
    Id = models.AutoField("层级编号", primary_key=True)
    BOM = models.ForeignKey(BOM, on_delete=models.CASCADE, verbose_name="物料清单")
    Level = models.IntegerField("层级", default=1)

    def __str__(self):
        return f"层级 {self.Level} - BOM {self.BOM.Id}"

    class Meta:
        app_label = app_name
        db_table = "[%s].[BOMLevel]" % schema
        verbose_name = 'BOM层级'
        verbose_name_plural = verbose_name