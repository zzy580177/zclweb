from django.db import models
from django_starter.db.base_models import *



app_name = "a_wuliao"  # 应用名称
schema = app_name


class Attribute(models.Model):
    """属性表"""
    attribute_id = models.AutoField("属性序号", primary_key=True)
    name = models.CharField("属性名称", max_length=max_charIdLen, unique=True)
    description = models.TextField("描述", null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        app_label = app_name
        db_table = f"[{schema}].[Attribute]"
        verbose_name = '1.0 基础属性管理'
        verbose_name_plural = verbose_name
        ordering = ['description', 'attribute_id']

class MaterialGroup(base_model):
    """物料组表"""
    GROUP_CHOICES = [("01", "成品机"), ("02", "半成品件"), ("03", "外购件"), ("04", "中间件")]
    SUB_GROUP_CHOICES = [
        ("01.01", "成品整机"),
        ("01.02", "成品夹具"),
        ("01.03", "客制模具"),
        ("01.04", "成品机部件"),
        ("02.01", "整机钣金件"),
        ("02.02", "夹具钣金件"),
        ("02.03", "整机机加件"),
        ("02.04", "夹具机加件"),
        ("02.05", "ZCL标准机加件"),
        ("02.06", "临时机加件"),
        ("02.07", "返工类机加件"),
        ("02.KZ", "客制模具"),
        ("03.01", "电器类"),
        ("03.02", "气动类"),
        ("03.03", "五金类"),
        ("03.04", "刀具类"),
        ("03.05", "其它类"),
    ]

    group_id = models.AutoField(primary_key=True, verbose_name="序号")
    name = models.CharField("名称", max_length=max_charNameLen)  
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
        related_name="children", verbose_name="父组", db_index=True)
    number = models.CharField("编号", max_length=max_charIdLen, null=True, blank=True)  
    level = models.IntegerField("层级", null=True, blank=True) 
    group = models.CharField("一级分类", max_length=max_charIdLen, null=True, blank=True, choices=GROUP_CHOICES) 
    sub_group = models.CharField("二级分类", max_length=max_charIdLen, null=True, blank=True, choices=SUB_GROUP_CHOICES)  
    min_group = models.CharField("三级分类", max_length=max_charIdLen, null=True, blank=True)  

    def __str__(self):
        if self.number:
            return f"{self.number}"
        return self.name

    def get_parent(self):
        """获取父组"""
        return self.parent

    def get_children(self):
        """获取所有子组"""
        return self.children.all()
    
    def save(self, *args, **kwargs):
        """覆盖 save 方法，自动分配未使用的 group_id"""
        if not self.group_id:
            # 使用AutoField自动分配ID，不需要手动处理
            pass
        super().save(*args, **kwargs)

    class Meta:
        abstract = False
        app_label = app_name
        db_table = f"[{schema}].[MaterialGroup]"
        verbose_name = '1.1 物料组管理'
        verbose_name_plural = verbose_name

class Material(base_model):
    """物料表"""
    material_id = models.AutoField("物料序号", primary_key=True)
    group = models.ForeignKey(MaterialGroup, 
        on_delete=models.CASCADE, verbose_name="物料组", related_name="materials")
    unit = models.ForeignKey(Attribute,
        on_delete=models.SET_NULL, null=True, blank=True, verbose_name="单位",
        limit_choices_to={'name': '单位'} )
    number = models.CharField("物料编号", max_length=max_charIdLen, unique=True, null=True, blank=True)
    name = models.CharField("物料名称", max_length=max_charNameLen)
    helpcode = models.CharField("助记码", max_length=max_charTextLen, null=True, blank=True)
    model = models.CharField("型号", max_length=max_charNameLen, null=True, blank=True)
    source = models.CharField("来源", max_length=255, null=True, blank=True)
    description = models.TextField("描述", null=True, blank=True)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        if self.number:
            return f"{self.name} {self.number}"
        return self.name
    class Meta:
        app_label = app_name
        db_table = f"[{schema}].[Material]"
        verbose_name = '1.2 物料管理'
        verbose_name_plural = verbose_name

class BomVersion(base_model):
    """BOM版本模型"""
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name="物料", related_name="bom_versions")
    version = models.CharField("版本号", max_length=max_charIdLen)
    base = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="基础版本", related_name="derived_versions")
    change_reason = models.TextField("变更原因", blank=True, null=True)
    status = models.CharField("状态", max_length=max_charStateLen, choices=BOM_STATUS_CHOICES, default='草稿')
    creator = models.CharField("创建人", max_length=max_charNameLen, null=True, blank=True)

    def __str__(self):
        return f"M{self.material.material_id} - {self.version}"
        
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['material_id', 'version'], name='pk_bomversion_composite')
        ]
        abstract = False
        app_label = app_name
        db_table = f"[{schema}].[BomVersion]"
        verbose_name = '1.3 BOM版本管理'
        verbose_name_plural = verbose_name
    

class Bom(base_model):
    version = models.ForeignKey(BomVersion, on_delete=models.CASCADE,
        verbose_name="BOM版本", related_name="details")
    p_material = models.ForeignKey(Material, on_delete=models.CASCADE, 
        null=True, blank=True, verbose_name="父物料", related_name="as_parent_boms")
    c_material = models.ForeignKey(Material, on_delete=models.CASCADE, 
        null=True, blank=True, verbose_name="子物料", related_name="as_child_boms")
    quantity = models.DecimalField("用量", max_digits=12,
        decimal_places=4, default=1.0000, validators=[MinValueValidator(0.0001)]
    )
    level = models.IntegerField("层级", default=1)
    remark = models.CharField("备注", max_length=max_charTextLen, blank=True, null=True)

    def save(self, *args, **kwargs):
         #if not self.bom_id and self.version.material:
         #    self._meta.get_field('bom_id').prefix = f'BOM_M{self.version.material.material_id}_'
         super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.bom_id}"

    class Meta:
        unique_together = ('version', 'p_material', 'c_material')
        app_label = app_name
        db_table = f"[{schema}].[BOM]"
        verbose_name = '1.4 BOM表管理'
        verbose_name_plural = verbose_name
