from django.db import models
from django.conf import settings

from django_starter.db.models import AbstractBaseModel, Attribute, Material, MaterialGroup, BOM

app_name = "bmui"  # 应用名称
schema = app_name

class Attribute(Attribute):
    """属性表"""
    class Meta:
        app_label = app_name
        db_table = f"[{schema}].[Attribute]"
        verbose_name = '基础属性管理'
        verbose_name_plural = verbose_name

class MaterialGroup(MaterialGroup):
    """物料组表"""
    class Meta:
        app_label = app_name
        db_table = f"[{schema}].[MaterialGroup]"
        verbose_name = '物料组管理'
        verbose_name_plural = verbose_name


class Material(Material):
    """物料表"""
    FId = models.IntegerField("物料序号", primary_key=True)  
    FGroup = models.ForeignKey(
        MaterialGroup,
        on_delete=models.CASCADE,
        verbose_name="物料组",
        related_name="materials"
    )  
    FNumber = models.CharField("物料编号", max_length=50, null=True, blank=True)  
    FName = models.CharField("物料名称", max_length=255)  
    FHelpCode = models.CharField("助记码", max_length=255, null=True, blank=True)  
    FModel = models.CharField("型号", max_length=255, null=True, blank=True)  
    FUnit = models.ForeignKey(
        Attribute,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="单位",
        limit_choices_to={'Description': '单位'} 
    )
    FSource = models.CharField("来源", max_length=255, null=True, blank=True)  
    FDescription = models.TextField("描述", null=True, blank=True)  

    def __str__(self):
        return f"{self.FName} ({self.FNumber})"
    
    def save(self, *args, **kwargs):
        """覆盖 save 方法，自动分配未使用的 FId"""
        if not self.FId:  # 如果未指定 FId
            existing_ids = set(MaterialGroup.objects.values_list('FId', flat=True))
            self.FId = next(i for i in range(1, max(existing_ids, default=0) + 2) if i not in existing_ids)
        super().save(*args, **kwargs)

    class Meta:
        app_label = app_name
        db_table = f"[{schema}].[Material]"
        verbose_name = '物料管理'
        verbose_name_plural = verbose_name


class BOM(AbstractBaseModel):
    """BOM 表"""
    Material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="child_boms", verbose_name="子物料")
    Quantity = models.DecimalField("数量", max_digits=10, decimal_places=2)
    Version = models.CharField("BOM版本号", max_length=50, null=True, blank=True)  # BOM 的版本号
    Description = models.TextField("备注", null=True, blank=True)

    def __str__(self):
        return f"{self.ParentMaterial} -> {self.ChildMaterial} ({self.Quantity})"

    class Meta:
        app_label = app_name
        db_table = "[%s].[BOM]" % schema
        verbose_name = '物料表管理'
        verbose_name_plural = verbose_name