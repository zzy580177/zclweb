from __future__ import unicode_literals
from django.db import models
from .urls import app_name

schema = "CNC700Cutting"
class Alarmi(models.Model):
	""""告警索引表"""
	#Id = models.IntegerField();
	AllarmID = models.SmallIntegerField('告警ID')
	AllarmString = models.CharField('告警信息',max_length=50, null=True, blank=True)
	TypeID = models.IntegerField(null=True, blank=True)
	Description_Id = models.IntegerField(null=True, blank=True)
	def __str__(self):
		return self.AllarmID
	class Meta:
		db_table = "[%s].[Alarmi]"% schema
		app_label = app_name
		ordering = ['AllarmID']
		verbose_name = '告警索引表'
		verbose_name_plural = verbose_name

class LiveState(models.Model):
	"""在线日志"""
	#Id = models.IntegerField();
	CellaID = models.IntegerField("设备编号",null=True, blank=True);
	Plant = models.CharField("物理位置",max_length=50,  blank=True);
	Check1 = models.DateTimeField("连线状态时间更新",null=True, blank=True);
	Check2 =  models.DateTimeField("掉线状态时间更新",null=True, blank=True);
	Note_Id = models.CharField("设备分类", max_length=50, blank=True);
	def __str__(self):
		return self.Check1
	class Meta:
		db_table = "[%s].[LiveState]"% schema
		app_label = app_name
		ordering = ['-Check1']
		verbose_name = '在线日志'
		verbose_name_plural = verbose_name

class Pezzi(models.Model):
	"""产量信息日志"""
	#Id = models.IntegerField();
	CellaID = models.IntegerField("设备编号",null=True, blank=True);
	Plant = models.CharField("物理位置",null=True,max_length=50);
	WorkSheetID = models.CharField("工单号",null=True, max_length =50);
	DataTime = models.CharField("时间",null=True, max_length =50); 
	Pezzi = models.IntegerField("生产工件数",null=True, blank=True);
	ReqPezzi = models.IntegerField("需求工件数",null=True, blank=True);
	ResidPezzi = models.IntegerField("待生产工件数",null=True, blank=True);
	PieceTime = models.IntegerField(null=True, blank=True);
	EstimatedTm = models.CharField("预计剩余时间",null=True, max_length=50);
	TotWorkTm = models.CharField(null=True, max_length=50);
	def __str__(self):
		return self.DataTime
	class Meta:
		db_table = "[%s].[Pezzi]"% schema
		app_label = app_name
		ordering = ['-DataTime']
		verbose_name = '产量信息日志'
		verbose_name_plural = verbose_name

class Stato(models.Model):
	"""工作状态切换日志"""
	#Id = models.IntegerField();
	CellaID = models.IntegerField("设备编号",null=True, blank=True);
	Plant = models.CharField("物理位置",max_length=50);
	WorkSheetID = models.CharField("工单号",null=True, max_length =50); 
	DataTime = models.CharField("时间",null=True, max_length =50); 
	stato_choics =(
		(True, "运行"),
		(False, "停止")
	)
	Stato = models.BooleanField("状态切换",null=True, blank=True, choices= stato_choics);
	Alarm = models.IntegerField('告警ID',null=True, blank=True);
	def __str__(self):
		return self.DataTime
	class Meta:
		db_table = "[%s].[Stato]"% schema
		app_label = app_name
		ordering = ['-DataTime']
		verbose_name = '工作状态切换日志'
		verbose_name_plural = verbose_name
		
class Order(models.Model):
	"""订单表"""
	#Id = models.IntegerField();
	CellaID = models.IntegerField("设备编号",null=True, blank=True);
	Plant = models.CharField("物理位置",max_length=50);
	WorkSheetID = models.CharField("工单号",null=True, max_length =50);	
	OrderID = models.CharField("订单号",null=True, max_length =50); 
	WorkStatus = models.CharField("工单状态",null=True, max_length =50); 
	Colour = models.CharField("产品颜色",null=True, max_length =50); 	
	Process = models.CharField("工序描述",null=True, max_length =50); 
	StytleNum = models.CharField("产品款号",null=True, max_length =50); 
	FinishParts = models.CharField("完成工件数",null=True, max_length =50); 
	RequireParts = models.CharField("需求工件数",null=True, max_length =50); 	
	AddReqParts = models.CharField("追加工件数",null=True, max_length =50); 
	def __str__(self):
		return self.WorkSheetID
	class Meta:
		db_table = "[%s].[Order]"% schema
		app_label = app_name
		ordering = ['WorkStatus']
		verbose_name = '订单表'
		verbose_name_plural = verbose_name
		
class OrderHistory(models.Model):
	#Id = models.IntegerField();
	CellaID = models.IntegerField("设备编号",null=True, blank=True);
	Plant = models.CharField("物理位置",max_length=50);
	WorkSheetID = models.CharField("工单号",null=True, max_length =50); 
	StartTime = models.CharField("开始时间",null=True, max_length =50); 
	StopTime = models.CharField("结束时间",null=True, max_length =50); 
	Status = models.CharField(null=True, max_length =50); 
	Mode = models.CharField("工作模式",null=True, max_length =50); 
	PowerOnTM = models.CharField("上电时长",null=True, max_length =50); 
	WorkingTM = models.CharField("加工时长",null=True, max_length =50); 
	FinishParts = models.CharField("完成工件数",null=True, max_length =50); 
	def __str__(self):
		return self.StartTime
	class Meta:
		db_table = "[%s].[OrderHistory]"% schema
		app_label = app_name
		ordering = ['-StartTime']
		verbose_name = '订单加工记录'
		verbose_name_plural = verbose_name

