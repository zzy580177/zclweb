from django.db import models
from apps.bmui.models import Attribute, Material
from django.conf import settings
from django_starter.db.models import Step, ProcessStep, ProcessRoute

app_name = "pmcui"  # 关联应用名称
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
        return self.OrderId+' '+ self.Product_id + ' ' + self.LotId
    class Meta:
        db_table = f"[{schema}].[POrder]"
        app_label = app_name
        verbose_name = '产品订单管理'
        verbose_name_plural = verbose_name

class PartsOrder(AbstractBaseModel):
    Id = models.AutoField("序号", primary_key=True);
    POrder = models.ForeignKey(POrder, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="订单号");
    Part = models.ForeignKey(Material, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="物料编号");
    Idex = models.IntegerField("零件序列号");
    Status = models.CharField("状态",max_length=50, null=True, blank=True);
    DeadLine = models.DateTimeField("交货日期",null=True, blank=True);
    Cost = models.DecimalField("成本", max_digits=10, decimal_places=2, null=True, blank=True);
    Quantity = models.DecimalField("数量", max_digits=10, decimal_places=2);
    Description = models.TextField("备注", null=True, blank=True);

    def __str__(self):
        return self.POrder.OrderId +" " + self.Part.FName
    class Meta:
        db_table = f"[{schema}].[PartsOrder]"
        app_label = app_name
        verbose_name = '产品订单详情管理'
        verbose_name_plural = verbose_name

class Step(Step):
    """"工序索引表"""
    def save(self, *args, **kwargs):
        if not self.Id:
            last = Step.objects.all().order_by('-Id').first()
            if last and last.Id.startswith('GX'):
                num = int(last.Id[2:]) + 1
            else:
                num = 1
            self.Id = f'GX{num:04d}'
        super().save(*args, **kwargs)

    class Meta:    
        db_table = "[%s].[Step]"% schema
        app_label = app_name
        verbose_name = '生产工序'
        verbose_name_plural = verbose_name

class ProcessStep(ProcessStep):
    """"工序配方表"""
    class Meta:
        db_table = "[%s].[ProcessStep]"% schema
        app_label = app_name
        verbose_name = '生产工序配方'
        verbose_name_plural = verbose_name

class ProcessRoute(ProcessRoute):
    """"工艺流程管理表"""
    class Meta:
        db_table = "[%s].[ProcessRoute]"% schema
        app_label = app_name
        verbose_name = '生产工艺流程'
        verbose_name_plural = verbose_name

class VirtualProcessRoute(ProcessRoute):
    steps = None  # 需要确保在使用前正确初始化

    class Meta:
        proxy = True
        app_label = app_name
        verbose_name = '工艺流程'
        verbose_name_plural = verbose_name

    def get_steps_list(self):
        """动态获取关联步骤列表"""
        if self.steps is None:
            # 如果 steps 未初始化，尝试通过关联模型动态获取
            self.steps = ProcessStep.objects.filter(Route_id=self.Id)  # 假设关联字段为 ProcessRoute
        return list(self.steps.all().order_by('SeqNum'))
    
    @property
    def formatted_steps(self):
        """返回结构化步骤数据"""
        steps_list = self.get_steps_list()
        return [{
            'SeqNum': step.SeqNum,
            'StepName': step.Step.Name,
            'EqpType': step.Step.EqpType,
            'params': step.Parameters
        } for step in steps_list]
