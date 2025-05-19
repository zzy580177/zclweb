from django.db import models
from django.conf import settings

app_name = "bmui"  # 应用名称
schema = app_name

class AbstractBaseModel(models.Model):
    """抽象基类，包含通用字段和方法"""
    CreateTime = models.DateTimeField("创建时间", auto_now_add=True)
    UpdateTime = models.DateTimeField("更新时间", auto_now=True)
    IsDelete = models.BooleanField("是否删除", default=False)
    IsActive = models.BooleanField("是否启用", default=True)

    def soft_delete(self):
        """逻辑删除"""
        self.IsDelete = True
        self.save(update_fields=["IsDelete", "UpdateTime"])

    def restore(self):
        """恢复逻辑删除"""
        self.IsDelete = False
        self.save(update_fields=["IsDelete", "UpdateTime"])

    class Meta:
        abstract = True


class Attribute(models.Model):
    """属性表"""
    Id = models.AutoField("属性序号", primary_key=True)
    Name = models.CharField("属性名称", max_length=255, unique=True)
    Description = models.TextField("描述", null=True, blank=True)

    def __str__(self):
        return self.Name

    class Meta:
        app_label = app_name
        db_table = f"[{schema}].[Attribute]"
        verbose_name = '基础属性管理'
        verbose_name_plural = verbose_name

class MaterialGroup(models.Model):
    """组表"""
    Id = models.AutoField("组序号", primary_key=True)
    Name = models.CharField("组名称", max_length=255)
    SubName = models.CharField("子组名称", max_length=255, null=True, blank=True)
    Description = models.TextField("描述", null=True, blank=True)
    def __str__(self):
        return self.Name  + self.SubName
    
    class  Meta:
        app_label = app_name
        db_table = f"[{schema}].[MaterialGroup]"
        verbose_name = '物料组管理'
        verbose_name_plural = verbose_name


class BaseMaterial(AbstractBaseModel):
    """基础物料表"""
    Id = models.CharField("物料编号", max_length=50, primary_key=True)
    Name = models.CharField("物料名称", max_length=255)
    Model = models.CharField("物料型号", max_length=255, null=True, blank=True)
    HelpCode = models.CharField("助记码", max_length=255, null=True, blank=True)
    Group = models.ForeignKey(MaterialGroup, on_delete=models.CASCADE, verbose_name="物料组")
    def __str__(self):
        return self.Name

    class Meta:
        app_label = app_name
        db_table = f"[{schema}].[BaseMaterial]"
        verbose_name = '基础物料'
        verbose_name_plural = verbose_name


class MaterialVersion(models.Model):
    """物料版本表"""
    Id = models.AutoField("版本序号", primary_key=True)
    BaseMaterial = models.ForeignKey(BaseMaterial, on_delete=models.CASCADE, verbose_name="基础物料")
    Version = models.CharField("版本号", max_length=50)  # 例如 V1.0, V2.0
    EffectiveDate = models.DateField("生效日期", null=True, blank=True)
    ExpiryDate = models.DateField("失效日期", null=True, blank=True)
    Description = models.TextField("版本描述", null=True, blank=True)

    def __str__(self):
        return f"{self.BaseMaterial.Name} - {self.Version}"

    class Meta:
        app_label = app_name
        db_table = "[%s].[MaterialVersion]" % schema
        verbose_name = '物料版本'
        verbose_name_plural = verbose_name
        unique_together = ("BaseMaterial", "Version")  # 同一物料编号不能有重复版本


class Material(AbstractBaseModel):
    """物料表"""
    Id = models.AutoField("物料序号", primary_key=True)
    MaterialVersion = models.ForeignKey(MaterialVersion, on_delete=models.CASCADE, verbose_name="物料版本")
    Type = models.ForeignKey(Attribute, on_delete=models.CASCADE, verbose_name="物料类型", related_name="type_materials")
    Source = models.ForeignKey(Attribute, on_delete=models.CASCADE, verbose_name="物料来源属性", related_name="source_materials")
    Attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, verbose_name="物料属性", related_name="attribute_materials", null=True, blank=True)
    Figure = models.TextField("图号", null=True, blank=True)
    Description = models.TextField("备注", null=True, blank=True)

    def __str__(self):
        return f"{self.MaterialVersion.BaseMaterial.Name} - {self.MaterialVersion.Version}"

    class Meta:
        app_label = app_name
        db_table = "[%s].[Material]" % schema
        verbose_name = '物料'
        verbose_name_plural = verbose_name


class BOM(AbstractBaseModel):
    """BOM 表"""
    ParentMaterial = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="parent_boms", verbose_name="父物料", null=True, blank=True)
    ChildMaterial = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="child_boms", verbose_name="子物料")
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