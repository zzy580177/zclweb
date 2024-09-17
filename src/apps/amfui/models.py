from __future__ import unicode_literals
from time import strftime, gmtime
from django.db import models
from .urls import app_name
from datetime import datetime, timedelta, date, time
import math

schema = "CNC700Cutting"
def getDailyQset(queryset, day):
	return queryset.filter( Day = day)
def sec2TmStr(sec):
	h = 0; d = 0; m,s = divmod(sec, 60)
	if m > 60:
		h,m = divmod(m, 60)
		if h > 24:
			d,h= divmod(h, 24)
			return str(int(d))+" Day %02d Hour" % h
		else:			
			return "%02d Hour %02d Min" % (h, m)
	return " %2d Min" % m
	



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
	Cell_id = models.IntegerField("设备编号",null=True, blank=True);
	Check1 = models.DateTimeField("连线状态时间更新",null=True, blank=True);
	Check2 =  models.DateTimeField("掉线状态时间更新",null=True, blank=True);
	TimeOff = models.FloatField(null=True, blank=True)
	OnLine = models.CharField("在线时长-s", max_length=20, blank=True);


	def __str__(self):
		return self.Check1
	class Meta:
		db_table = "[%s].[LiveState]"% schema
		app_label = app_name
		ordering = ['-Check1', '-Check2']
		verbose_name = '设备在线日志'
		verbose_name_plural = verbose_name

class LiveStateManage(LiveState):
	class Meta:
		proxy = True
		app_label = app_name
		verbose_name = '设备在线管理'
		verbose_name_plural = verbose_name
	
	def date(self):
		return self.Check1.strftime("%Y-%m-%d")

class Pezzi(models.Model):
	"""产量信息日志"""
	#Id = models.IntegerField();
	Cell_id = models.IntegerField("设备编号",null=True, blank=True);
	WorkSheetID = models.CharField("工单号",null=True, max_length =50);
	Data = models.CharField("日期",null=True, max_length =20); 
	DataTime = models.CharField("时间",null=True, max_length =20); 
	Pezzi = models.IntegerField("生产工件数",null=True, blank=True);
	ReqPezzi = models.IntegerField("需求工件数",null=True, blank=True);
	ResidPezzi = models.IntegerField("待生产工件数",null=True, blank=True);
	PieceTime = models.IntegerField(null=True, blank=True);
	EstimatedTm = models.CharField("预计剩余时间",null=True, max_length=20);
	TotWorkTm = models.CharField(null=True, max_length=10);
	def __str__(self):
		return self.DataTime
	class Meta:
		db_table = "[%s].[Pezzi]"% schema
		app_label = app_name
		ordering = ['-DataTime']
		verbose_name = '生产信息日志'
		verbose_name_plural = verbose_name

class Stato(models.Model):
	"""工作状态切换日志"""
	#Id = models.IntegerField();
	Cell_id = models.IntegerField("设备编号",null=True, blank=True);
	WorkSheetID = models.CharField("工单号",null=True, max_length =50); 
	Data = models.CharField("日期",null=True, max_length =20); 
	DataTime = models.CharField("时间",null=True, max_length =20); 
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
		verbose_name = '设备状态切换表'
		verbose_name_plural = verbose_name
		
class Cell(models.Model):
	status_choics = ( ('0', '作业'), ('-1', '待机'), ('-2', '离线'), ('*' , '异常'))
	type_choics = ((1, "新代系统"), (2, "PLC"))
	CellID = models.IntegerField("设备编号",null=True, blank=True);
	Plant = models.CharField("车间", max_length=40, blank=True);
	Name = models.CharField("设备名称", max_length=40, blank=True);
	Type = models.IntegerField(verbose_name="系统", null=True, blank=True, choices= type_choics)
	Status = models.CharField(verbose_name="当前状态", max_length=10, blank=True, choices= status_choics) 
	IP = models.CharField("设备IP", max_length=20, blank=True);
	Create = models.DateTimeField("创建日期",null=True, blank=True);
	OnLine = models.FloatField("在线时长", null=True, blank=True);
	WorkTM = models.FloatField("作业时长", null=True, blank=True);

	def OnLineStr(self):
		return sec2TmStr(self.OnLine)
	def WorkTMStr(self):
		return sec2TmStr(self.WorkTM)

	OnLineStr.short_description = '在线时长'
	WorkTMStr.short_description = '作业时长'
	def __str__(self):
		return self.CellID
	class Meta:
		db_table = "[%s].[Cell]"% schema
		app_label = app_name
		verbose_name = '设备管理表'
		verbose_name_plural = verbose_name

class Record(models.Model):
	#Id = models.IntegerField();
	Cell_id = models.IntegerField("设备编号",null=True, blank=True);
	WorkSheetID = models.CharField("工单号",null=True, max_length =50);	
	Date = models.CharField("日期",null=True, max_length =20);
	StartTime = models.CharField("开始时间",null=True, max_length =20);
	StopTime = models.CharField("结束时间",null=True, max_length =20);
	Status = models.CharField(null=True, max_length =20); 
	Mode = models.CharField("工作模式",null=True, max_length =20); 
	PowerOnTM = models.CharField("上电时长",null=True, max_length =20); 
	WorkingTM = models.CharField("加工时长",null=True, max_length =20); 
	FinishParts = models.IntegerField("完成工件数",null=True, blank=True);
	IdleTMSec = models.FloatField(null=True, blank=True);
	PowerOnSec = models.FloatField(null=True, blank=True);
	WorkingSec = models.FloatField(null=True, blank=True);
	def tot_PowerOnSec (self):
		return #self.model.objects.filter(Date=self.Date, Cell_id= self.Cell_id).aggregate(tot_PowerOnSec = Sum('PowerOnSec'))
	def __str__(self):
		return self.Date
	class Meta:
		db_table = "[%s].[Record]"% schema
		app_label = app_name
		ordering = ['-StartTime']
		verbose_name = '加工记录'
		verbose_name_plural = verbose_name		

class RecordManage(Record):
	class Meta:
		proxy = True
		app_label = app_name
		verbose_name = '加工记录管理'
		verbose_name_plural = verbose_name

class WorkSheet(models.Model):
	"""订单表"""
	Id = models.IntegerField();
	Cell_id = models.IntegerField("设备编号",null=True, blank=True, editable=False);
	Order_id = models.IntegerField("订单序列号",null=True, blank=True, editable=False);
	WorkSheetID = models.CharField("工单号",null=True, max_length =50, editable=False);	
	OrderID = models.CharField("订单号",null=True, max_length =50, editable=False); 
	Status = models.CharField("工单状态",null=True, max_length =20, editable=False); 
	ProcessID = models.CharField("工序备注",null=True, max_length =50); 
	FinishParts = models.IntegerField("完成工件数",null=True, blank=True, editable=False); 
	ReqParts = models.IntegerField("需求工件数",null=True, blank=True, editable=False); 	
	AddReqParts = models.IntegerField("追加工件数",null=True, blank=True, editable=False); 
	def __str__(self):
		return self.WorkSheetID
	class Meta:
		db_table = "[%s].[WorkSheet]"% schema
		app_label = app_name
		ordering = ['Status']
		verbose_name = '工单表'
		verbose_name_plural = verbose_name

class Order(models.Model):
	"""订单表"""
	#Id = models.IntegerField();	
	OrderID = models.CharField("订单号",null=True, max_length =50, editable=False); 
	Status = models.CharField("订单状态",null=True, max_length =20, editable=False); 
	Colour = models.CharField("产品颜色",null=True, max_length =50);
	ProductID = models.CharField("产品款号",null=True, max_length =50); 
	ReqParts = models.IntegerField("需求工件数",null=True, blank=True, editable=False); 	
	def __str__(self):
		return self.WorkSheetID
	class Meta:
		db_table = "[%s].[Order]"% schema
		app_label = app_name
		ordering = ['OrderID']
		verbose_name = '订单表'
		verbose_name_plural = verbose_name
    