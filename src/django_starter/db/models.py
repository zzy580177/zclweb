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
# Create your models here.
class Step(models.Model):
	""""工序索引表"""
	Id = models.SmallIntegerField("工序编号", primary_key=True); 
	Name = models.CharField('工序名称',max_length =40)
	EqpType = models.IntegerField('类别',null=True, blank=True)
	Description = models.IntegerField('备注索引',null=True, blank=True)
	def __str__(self):
		return str(self.Id) + " " + self.Name 
	class Meta:
		abstract = True
		db_table = "[%s].[Step]"% schema
		verbose_name = '工序索引表'
		verbose_name_plural = verbose_name
		
class ProcessStep(models.Model):
	""""工序配方表"""
	StepId = models.SmallIntegerField("工艺配方编号", primary_key=True); 
	Step = models.ForeignKey('Step', on_delete=models.CASCADE, null=True,blank=True, verbose_name = '工序')
	Route = models.ForeignKey('ProcessRoute', on_delete=models.CASCADE, null=True,blank=True, verbose_name = '工艺流程')
	Parameters = models.JSONField ('参数', null = True, blank= True)
	SeqNum = models.IntegerField('工序序列号',null=True, blank=True)
	Description = models.IntegerField('备注索引',null=True, blank=True)
	def __str__(self):
		return str(self.Id) + " " + self.StepId + " " + self.Step_Name
	class Meta:
		abstract = True
		db_table = "[%s].[ProcessStep]"% schema
		verbose_name = '工艺配方表'
		verbose_name_plural = verbose_name

class ProcessRoute(models.Model):
	""""工艺流程管理表"""
	Id = models.SmallIntegerField("工艺流程编号", primary_key=True);
	Product_id = models.CharField("款号", max_length =50); 
	ApprovalStatus = models.CharField ('状态', max_length =40);	
	Version = models.SmallIntegerField ('版本', null = True, blank= True);
	StartDay = models.DateField ('创建日期', null = True, blank= True);
	Description = models.IntegerField('备注索引',null=True, blank=True)
	def __str__(self):
		return str(self.Id) + " " + self.Product_id + "工艺流程" 
	class Meta:
		abstract = True
		db_table = "[%s].[ProcessRoute]"% schema
		verbose_name = '工艺流程管理表'
		verbose_name_plural = verbose_name
