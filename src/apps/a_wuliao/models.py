from django.db import models
from django_starter.db.base_models import *

app_name = "a_wuliao"  # 应用名称
schema = app_name


class Attribute(Attribute):
    """属性表"""
    class Meta:
        abstract = False
        app_label = app_name
        db_table = f"[{schema}].[Attribute]"
        verbose_name = '1.0 基础属性管理'
        verbose_name_plural = verbose_name
        ordering = ['description', 'attribute_id']

class MaterialGroup(MaterialGroup):
    """物料组表"""
    class Meta:
        abstract = False
        app_label = app_name
        db_table = f"[{schema}].[MaterialGroup]"
        verbose_name = '1.1 物料组管理'
        verbose_name_plural = verbose_name

class Material(base_model):
    """物料表"""
    material_id = models.AutoField("物料序号", primary_key=True)
    group = models.ForeignKey(MaterialGroup, on_delete=models.CASCADE, 
        verbose_name="物料组", related_name="materials")
    number = models.CharField("物料编号", max_length=max_charIdLen, null=True, blank=True)
    name = models.CharField("物料名称", max_length=max_charNameLen)
    helpcode = models.CharField("助记码", max_length=max_charTextLen, null=True, blank=True)
    model = models.CharField("型号", max_length=max_charNameLen, null=True, blank=True)
    unit = models.ForeignKey(
        Attribute,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="单位",
        limit_choices_to={'name': '单位'}
    )
    source = models.CharField("来源", max_length=255, null=True, blank=True)
    description = models.TextField("描述", null=True, blank=True)

    def __str__(self):
        if self.number:
            return f"{self.name} {self.number}"
        return self.name
    
    def save(self, *args, **kwargs):
        """覆盖 save 方法，使用AutoField自动分配ID"""
        super().save(*args, **kwargs)

    class Meta:
        abstract = False
        app_label = app_name
        db_table = f"[{schema}].[Material]"
        verbose_name = '1.2 物料管理'
        verbose_name_plural = verbose_name

class BomVersion(base_model):
    """BOM版本模型"""
    version_id = AutoCodeField(prefix='BOM_', primary_key=True, editable=False, verbose_name="版本ID")
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name="物料", related_name="bom_versions")
    version = models.CharField("版本号", max_length=max_charIdLen)
    base = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="基础版本", related_name="derived_versions")
    change_reason = models.TextField("变更原因", blank=True, null=True)
    status = models.CharField("状态", max_length=max_charStateLen, choices=BOM_STATUS_CHOICES, default='草稿')
    creator = models.CharField("创建人", max_length=max_charNameLen, null=True, blank=True)
    
    class Meta:
        abstract = False
        app_label = app_name
        db_table = f"[{schema}].[BomVersion]"
        verbose_name = '1.3 BOM版本管理'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.version_id}"
    
    def save(self, *args, **kwargs):
        if not self.version_id and self.material:
            self._meta.get_field('version_id').prefix = f'BOM_M{self.material.material_id}_'
        super().save(*args, **kwargs)

class Bom(base_model):
    bom_id = AutoCodeField(prefix='BOM_', length=5, primary_key=True, editable=False, verbose_name="BOM ID")
    version = models.ForeignKey(
        BomVersion, on_delete=models.CASCADE, verbose_name="BOM版本", related_name="details")
    p_material = models.ForeignKey(
        Material, on_delete=models.CASCADE, verbose_name="父物料", related_name="as_parent_boms")
    c_material = models.ForeignKey(
        Material, on_delete=models.CASCADE, verbose_name="子物料", related_name="as_child_boms")
    quantity = models.DecimalField("用量", max_digits=12,
        decimal_places=6, default=1.000000, validators=[MinValueValidator(0.000001)]
    )
    level = models.IntegerField("层级", default=1)
    remark = models.CharField("备注", max_length=max_charTextLen, blank=True, null=True)

    class Meta:
        abstract = False
        app_label = app_name
        db_table = f"[{schema}].[BOM]"
        verbose_name = '1.4 BOM表管理'
        verbose_name_plural = verbose_name


    def __str__(self):
        if self.p_material and self.c_material:
            return f"{self.p_material} -> {self.c_material} (x{self.quantity})"
        return f"BOM {self.bom_id}"
