from django.db import models

# Create your models here.
from django.db import models
from django_starter.db.base_models import *
from apps.a_wuliao.models import Attribute, Material, BomVersion

app_name = "c_gongyi"  # 关联应用名称
schema = app_name

# 审批状态选项
APPROVAL_STATUS_CHOICES = [
    ('draft', '草稿'),
    ('approved', '已批准'),
    ('rejected', '已拒绝'),
]

class MaterialParm(models.Model):    
    bom_ver = models.ForeignKey(BomVersion, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="物料版本")
    size = models.CharField("加工尺寸", max_length=50, null=True, blank=True)
    stuff = models.CharField("材料", max_length=50, null=True, blank=True)
    cost = models.DecimalField("材料成本", max_digits=10, decimal_places=2, null=True, blank=True)
    surface = models.CharField("表面处理", max_length=50, null=True, blank=True)
    description = models.TextField("备注", null=True, blank=True)

    def __str__(self):
        stuff = self.stuff or ''
        size = self.size or ''
        return f"{stuff} {size}".strip()
    
    class Meta:
        db_table = "[%s].[MaterialParm]"% schema
        app_label = app_name
        verbose_name = '3.0 工艺参数'
        verbose_name_plural = verbose_name

class Step(base_model):
    """工序索引表"""
    name = models.CharField('工序名称', max_length=40)
    type = models.ForeignKey(Attribute, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="工序分类", limit_choices_to={'description': '工序分类'})
    ucost = models.DecimalField('工序计件单价/元', max_digits=10, decimal_places=2, null=True, blank=True)
    hcost = models.DecimalField('工序计时单价/元', max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField("备注", null=True, blank=True)
    
    def __str__(self):
        return f"{self.name or ''}".strip()
    
    class Meta:
        unique_together = ('name', 'type')
        db_table = f"[{schema}].[Step]"
        app_label = app_name
        verbose_name = '3.1 工序管理'
        verbose_name_plural = verbose_name
        
class Process(base_model):
    """工序配方表"""  
    route = models.ForeignKey(
        'Route',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='工艺流程',
        related_name='main_steps'
    )
    subroute = models.ForeignKey(
        'Route',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='CNC工艺流程',
        related_name='sub_steps'
    )
    seqnum = models.IntegerField('工序序列号', null=True, blank=True)
    steps = models.ManyToManyField(
        'Step', 
        blank=True,
        verbose_name='工序列表',
        through='Craft')
    params = models.JSONField('参数', null=True, blank=True)
    description = models.TextField('备注', null=True, blank=True)
    
    def __str__(self):
        return str(self.seqnum)
    
    class Meta:
        unique_together = ('route', 'seqnum')
        db_table = "[%s].[Process]"% schema
        app_label = app_name
        verbose_name = '3.2 工艺卡'
        verbose_name_plural = verbose_name

class Craft(models.Model):
    process = models.ForeignKey('Process', on_delete=models.CASCADE, verbose_name="工序流程")
    step = models.ForeignKey('Step', on_delete=models.CASCADE, verbose_name="工序")
    params = models.TextField('参数', null=True, blank=True)
    
    class Meta:
        db_table = "[%s].[Craft]"% schema
        app_label = app_name
        verbose_name = '3.2.1 工艺配方'
        verbose_name_plural = verbose_name

class Route(base_model):
    """工艺流程管理表"""
    bom_ver = models.ForeignKey(BomVersion, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="物料版本")
    is_cnc = models.BooleanField('是否CNC工艺流程', default=False)
    product_id = models.CharField("款号", max_length=50) 
    approval_status = models.CharField('状态', max_length=40, choices=APPROVAL_STATUS_CHOICES, default='draft')    
    params = models.JSONField('参数', null=True, blank=True)
    description = models.TextField('备注索引', null=True, blank=True)
    
    def __str__(self):
        return f"{'CNC' if self.is_cnc else ''}工艺流程 {self.bom_ver}".strip()
    
    class Meta:
        unique_together = ('bom_ver', 'is_cnc')
        db_table = "[%s].[Route]"% schema
        app_label = app_name
        verbose_name = '3.3 工艺流程'
        verbose_name_plural = verbose_name

class VirtualProcessRoute(Route):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.steps = None

    class Meta:
        proxy = True
        app_label = app_name
        verbose_name = '3.4 流程管理'
        verbose_name_plural = verbose_name

    def get_steps_list(self):
        """动态获取关联步骤列表"""
        if self.steps is None:
            self.steps = Process.objects.filter(route_id=self.id)
        return list(self.steps.all().order_by('seqnum'))
    
    @property
    def formatted_steps(self):
        """返回结构化步骤数据"""
        steps_list = self.get_steps_list()
        return [{
            'SeqNum': step.seqnum,
            'StepName': step.step.name if step.step else '',
            'EqpType': step.step.type.name if step.step and step.step.type else '',
            'params': step.params
        } for step in steps_list]
