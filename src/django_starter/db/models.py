from django.db import models
from django.utils import timezone


class ModelManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(is_deleted=False)


class ModelExt(models.Model):
    objects = ModelManager()
    is_deleted = models.BooleanField('软删除标志', default=False)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        abstract = True

from django.conf import settings

schema = settings.DATABASES["default"].get("SCHEMA", "default_schema")
bmuiAppName = 'bmui'
pmcuiAppName = 'pmcui'
scgAppName = 'jihuaManagerUI'  # 假设这是另一个应用的名称
# Create your models here.


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
        unique_together = ('Name', 'Description')
        abstract = True
        db_table = "[%s].[Attribute]"% bmuiAppName
        app_label = bmuiAppName
        verbose_name = '属性表'
        verbose_name_plural = verbose_name

class MaterialGroup(models.Model):
    """物料组表"""
    FId = models.IntegerField("组序号", primary_key=True)
    FName = models.CharField("组名称", max_length=255)  
    FParent = models.ForeignKey(
        'self',  # 自关联
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="父组")
    FNumber = models.CharField("组编号", max_length=50, null=True, blank=True)  
    FLevel = models.IntegerField("层级", null=True, blank=True) 
    FClass_choics =(("01", "成品机"),("02", "半成品件"),("03", "外购件"),("04", "中间件")) 
    FClass = models.CharField("分类", max_length=50, null=True, blank=True, choices=FClass_choics)  
    FGroupCode_choics = (
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
    )
    FGroupCode = models.CharField("组代码", max_length=50, null=True, blank=True, choices=FGroupCode_choics)  
    FSubGroupCode = models.CharField("子组代码", max_length=50, null=True, blank=True)  

    def __str__(self):
        return f"{self.FName} ({self.FNumber})"

    def get_parent(self):
        """获取父组"""
        return self.Parent

    def get_children(self):
        """获取所有子组"""
        return self.children.all()
    
    def save(self, *args, **kwargs):
        """覆盖 save 方法，自动分配未使用的 FId"""
        if not self.FId:  # 如果未指定 FId
            existing_ids = set(MaterialGroup.objects.values_list('FId', flat=True))
            self.FId = next(i for i in range(1, max(existing_ids, default=0) + 2) if i not in existing_ids)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        db_table = f"[{bmuiAppName}].[MaterialGroup]"
        app_label = bmuiAppName
        verbose_name = '物料组管理'
        verbose_name_plural = verbose_name


class Material(AbstractBaseModel):
    """物料表"""
    FId = models.IntegerField("物料序号", primary_key=True);
    FGroup = models.ForeignKey(
        MaterialGroup,
        on_delete=models.CASCADE,
        verbose_name="物料组",
        related_name="materials"
    );
    FNumber = models.CharField("物料编号", max_length=50, null=True, blank=True);  
    FName = models.CharField("物料名称", max_length=255);
    FHelpCode = models.CharField("助记码", max_length=255, null=True, blank=True);  
    FModel = models.CharField("型号", max_length=255, null=True, blank=True);  
    FUnit = models.ForeignKey(
        Attribute,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="单位",
        limit_choices_to={'Description': '单位'} 
    );
    FSource = models.CharField("来源", max_length=255, null=True, blank=True);  
    FDescription = models.TextField("描述", null=True, blank=True);  
    FParent = models.ForeignKey(
        'self',null=True, blank=True,
        on_delete=models.CASCADE,
        verbose_name="中间件",
        related_name="parents"
    );

    def __str__(self):
        return f"{self.FName} ({self.FNumber})"
    
    def save(self, *args, **kwargs):
        """覆盖 save 方法，自动分配未使用的 FId"""
        if not self.FId:  # 如果未指定 FId
            existing_ids = set(MaterialGroup.objects.values_list('FId', flat=True))
            self.FId = next(i for i in range(1, max(existing_ids, default=0) + 2) if i not in existing_ids)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        db_table = f"[{bmuiAppName}].[Material]"
        app_label = bmuiAppName
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
        abstract = True
        db_table = "[%s].[BOM]" % bmuiAppName
        app_label = bmuiAppName
        verbose_name = '物料表管理'
        verbose_name_plural = verbose_name

class Step(models.Model):
    """"工序索引表"""
    Id = models.CharField("工序编号", max_length=8, primary_key=True)  # 改为 CharField
    Name = models.CharField('工序名称',max_length =40)
    EqpType = models.ForeignKey(Attribute, on_delete=models.SET_NULL, null=True,blank=True,
        verbose_name="工序分类",limit_choices_to={'Description': '工序分类'} );
    UCost = models.DecimalField('工序计件单价/元', max_digits=10, decimal_places=2, null=True, blank=True)
    HCost = models.DecimalField('工序计时单价/元', max_digits=10, decimal_places=2, null=True, blank=True)
    Description = models.IntegerField('备注索引',null=True, blank=True)
    def __str__(self):
        return self.Id + " " + self.Name 

    class Meta:
        abstract = True
        
class ProcessStep(models.Model):
    """"工序配方表"""
    PFId = models.AutoField("工艺配方编号", primary_key=True)
    
    Steps = models.ManyToManyField(
        'Step', 
        blank=True,
        verbose_name='工序列表',
        through='ProcessStepSteps'  # Add explicit through model
    )

    Route = models.ForeignKey(
        'ProcessRoute',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='工艺流程',
        related_name='main_steps'
    )
    subRoute = models.ForeignKey(
        'ProcessRoute',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='CNC工艺流程',
        related_name='sub_steps'
    )
    Parameters = models.JSONField('参数', null=True, blank=True)
    SeqNum = models.IntegerField('工序序列号', null=True, blank=True)
    Description = models.TextField('备注', null=True, blank=True)
    
    def __str__(self):
        return str(self.PFId)  # Updated to use PFId since Id doesn't exist
    
    class Meta:
        unique_together = ('Route', 'SeqNum')
        abstract = True

# Add explicit through model for Steps relationship
class ProcessStepSteps(models.Model):
    processstep = models.ForeignKey('ProcessStep', on_delete=models.CASCADE)
    step = models.ForeignKey('Step', on_delete=models.CASCADE)
    parameters = models.TextField('参数', null=True, blank=True)  # 新增字段

    
    class Meta:
        db_table = 'ProcessStepSteps'  # Explicit table name without underscore prefix
        abstract = True

class ProcessRoute(models.Model):
    """"工艺流程管理表"""
    Id = models.AutoField("工艺流程编号", primary_key=True);
    Product_id = models.CharField("款号", max_length =50); 
    Material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="物料编号");
    ApprovalStatus = models.CharField ('状态', max_length =40);    
    Version = models.SmallIntegerField ('版本', null = True, blank= True);
    StartDay = models.DateField ('创建日期', null = True, blank= True);
    Parameters = models.JSONField ('参数', null = True, blank= True);
    IsCNC = models.BooleanField('是否CNC工艺流程', default=False);
    Description = models.TextField('备注索引',null=True, blank=True)
    def __str__(self):
        return self.Material + "工艺流程 V" + self.Version
    class Meta:
        unique_together = ('Material', 'Version', 'IsCNC')
        abstract = True

class POrder(AbstractBaseModel):
    """订单表"""
    OrderId = models.CharField("订单号",max_length =50, primary_key=True); 
    Status = models.CharField("订单状态",max_length=50, null=True, blank=True);
    Product_id = models.CharField("产品编号",max_length=50, null=True, blank=True);
    DeadLine = models.DateTimeField("交货日期",null=True, blank=True);
    Owner = models.CharField("制单员",max_length=50, null=True, blank=True);
    WH = models.CharField("仓库员",max_length=50, null=True, blank=True);
    Audit = models.CharField("审计员",max_length=50, null=True, blank=True);
    Cost = models.DecimalField("成本", max_digits=10, decimal_places=2, null=True, blank=True)
    LotId = models.CharField("批次号", max_length=50, null=True, blank=True);
    Description = models.TextField("备注", null=True, blank=True); 

    def __str__(self):
        return self.OrderId
    class Meta:
        unique_together = ('Product_id', 'LotId')
        abstract = True
        db_table = f"[{scgAppName}].[POrder]"
        app_label = scgAppName
        verbose_name = '产品订单管理'
        verbose_name_plural = verbose_name

class PartsOrder(AbstractBaseModel):
    Id = models.AutoField("序号", primary_key=True);
    POrder = models.ForeignKey(POrder, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="订单号");
    Part = models.ForeignKey(Material, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="物料编号");
    Status = models.CharField("状态",max_length=50, null=True, blank=True);
    DeadLine = models.DateTimeField("交货日期",null=True, blank=True);
    Cost = models.DecimalField("成本", max_digits=10, decimal_places=2, null=True, blank=True);
    Quantity = models.DecimalField("数量", max_digits=10, decimal_places=2);
    Description = models.TextField("备注", null=True, blank=True);

    def __str__(self):
        return self.POrder.OrderId +" " + self.Part.FName
    class Meta:
        unique_together = ('POrder', 'Part')
        abstract = True

class MaterialParm(models.Model):
    Id = models.AutoField("序号", primary_key=True);
    Material = models.ForeignKey(Material, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="物料编号");
    Size = models.CharField("加工尺寸",max_length=50, null=True, blank=True);
    Stuff = models.CharField("材料",max_length=50, null=True, blank=True);
    Cost = models.DecimalField("材料成本", max_digits=10, decimal_places=2, null=True, blank=True);
    Surface = models.CharField("表面处理", max_length=50, null=True, blank=True);
    Description = models.TextField("备注", null=True, blank=True);

    def __str__(self):
        return self.Stuff +" " + self.Size
    class Meta:
        abstract = True
