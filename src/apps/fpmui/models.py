from django.db import models
from django.conf import settings
from django_starter.db.models import Step, ProcessStep, ProcessRoute

schema = 'fpmui'
app_name = 'fpmui'
# Create your models here.
class Step(Step):
	""""工序索引表"""
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
		verbose_name = '工序配方'
		verbose_name_plural = verbose_name

class ProcessRoute(ProcessRoute):
	""""工艺流程管理表"""
	class Meta:
		db_table = "[%s].[ProcessRoute]"% schema
		app_label = app_name
		verbose_name = '工艺流程'
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
