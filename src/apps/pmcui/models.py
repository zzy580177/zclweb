from django.db import models
from django.conf import settings
from django_starter.db.models import Step, ProcessStep, ProcessRoute, AbstractBaseModel, PartsOrder, MaterialParm, ProcessStepSteps
from apps.jihuaManagerUI.models import POrder

app_name = "pmcui"  # 关联应用名称
schema = app_name



class PartsOrder(PartsOrder):
    """产品订单详情"""
    class Meta:
        db_table = f"[{schema}].[PartsOrder]"
        app_label = app_name
        verbose_name = '产品详情列表'
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

class ProcessStepSteps(ProcessStepSteps):
    """"工序配方表"""
    class Meta:
        db_table = "[%s].[ProcessStepSteps]"% schema
        app_label = app_name
        verbose_name = '工序列表'
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

class MaterialParm(MaterialParm):
    """物料参数表"""
    class Meta:
        db_table = "[%s].[MaterialParm]"% schema
        app_label = app_name
        verbose_name = '生产参数管理'
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
