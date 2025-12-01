from django.db import models

# Create your models here.
from django.db import models
from django_starter.db.base_models import *
from apps.a_wuliao.models import Attribute, BomVersion

app_name = "c_gongyi"  # 关联应用名称
schema = app_name

# 审批状态选项
APPROVAL_STATUS_CHOICES = [
    ('draft', '草稿'),
    ('approved', '已批准'),
    ('rejected', '已拒绝'),
]

class MaterialParm(models.Model):
    bom_ver = models.OneToOneField(BomVersion, on_delete=models.CASCADE, verbose_name="物料版本")
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

class Process(models.Model):
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
    route_ver = models.CharField('工艺流程版本', max_length=10, null=True, blank=True)
    is_cnc = models.BooleanField('是否CNC工艺流程', default=False)
    product_id = models.CharField("款号", max_length=50)
    approval_status = models.CharField('状态', max_length=40, choices=APPROVAL_STATUS_CHOICES, default='draft')
    params = models.JSONField('参数', null=True, blank=True)
    description = models.TextField('备注索引', null=True, blank=True)

    def __str__(self):
        return f"{'CNC' if self.is_cnc else ''}工艺流程 {self.bom_ver}".strip()

    class Meta:
        unique_together = ('bom_ver','route_ver','is_cnc')
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


# CNC专用模型

class CNCProcess(base_model):
    """CNC工序卡片表"""
    route = models.ForeignKey(
        'Route', on_delete=models.CASCADE, null=True, blank=True, verbose_name='CNC工艺流程', related_name='cnc_processes'
    )
    seqnum = models.IntegerField('工序号', null=True, blank=True)
    steps = models.ManyToManyField('Step', blank=True, verbose_name='工步列表', through='CNCCraft')
    params = models.JSONField('参数', null=True, blank=True)
    description = models.TextField('备注', null=True, blank=True)

    def __str__(self):
        return f"CNC工序 {self.route.bom_ver}-V{self.route.route_ver}-{self.seqnum or ''}".strip()

    class Meta:
        unique_together = ('route', 'seqnum')
        db_table = f"[{schema}].[CNCProcess]"
        app_label = app_name
        verbose_name = '4.1 CNC工序'
        verbose_name_plural = verbose_name


class CNCProgram(base_model):
    """CNC程序表"""
    cnc_process = models.ForeignKey('CNCProcess', on_delete=models.CASCADE, related_name='programs', verbose_name="CNC工序")
    program_name = models.CharField('程序名称', max_length=100, help_text="CNC程序文件名")
    equipment_model = models.CharField('设备型号', max_length=50, null=True, blank=True)
    fixture_name = models.CharField('夹具名称', max_length=50, null=True, blank=True)
    simulation_time = models.IntegerField('模拟时间(分)', null=True, blank=True)
    description = models.TextField('备注', null=True, blank=True)
    path = models.CharField('程序路径', max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.program_name}"

    class Meta:
        db_table = f"[{schema}].[CNCProgram]"
        app_label = app_name
        verbose_name = '4.3 CNC程序'
        verbose_name_plural = verbose_name


class CNCCraft(models.Model):
    """CNC工步详情表"""
    process = models.ForeignKey('CNCProcess', on_delete=models.CASCADE, related_name='work_steps', verbose_name="工序卡片")
    step_num = models.IntegerField('工步序号', help_text="工步在工序中的顺序")
    step = models.ForeignKey('Step', on_delete=models.CASCADE, verbose_name="工步")
    params = models.JSONField('参数', null=True, blank=True, help_text="存储刀具、速度等参数的JSON数据")

    def __str__(self):
        return f"工序{self.step_num}: {self.step.name}"

    class Meta:
        unique_together = ('process', 'step_num')
        db_table = f"[{schema}].[CNCCraft]"
        app_label = app_name
        verbose_name = '4.2 CNC工步详情'
        verbose_name_plural = verbose_name
