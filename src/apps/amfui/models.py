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
	Name = models.CharField('设备类型',max_length =40)
	AlarmID = models.CharField('告警ID',max_length =10)
	AlarmString = models.CharField('告警信息',max_length=50)
	TypeID = models.IntegerField('类别',null=True, blank=True)
	Description_Id = models.IntegerField('备注索引',null=True, blank=True)
	def __str__(self):
		return str(self.Id) + " " + self.AlarmString
	class Meta:
		db_table = "[%s].[Alarmi]"% schema
		app_label = app_name
		verbose_name = '告警索引表'
		verbose_name_plural = verbose_name

class LiveState(models.Model):
	"""在线日志"""
	Cell = models.ForeignKey('Cell', on_delete=models.CASCADE, null=True,blank=True)
	Check1 = models.DateTimeField("连线状态时间更新");
	Check2 =  models.DateTimeField("掉线状态时间更新",null=True, blank=True);
	WorkSheet = models.ForeignKey('WorkSheet', on_delete=models.CASCADE, null=True,blank=True)
	OnLine = models.FloatField("在线时长-s", null=True, blank=True);

	def __str__(self):
		return self.Cell_Name + str(self.Cell_id)  + " " + self.Check1.strftime("%Y-%m-%d") 
	class Meta:
		db_table = "[%s].[LiveState]"% schema
		app_label = app_name
		verbose_name = '设备在线日志'
		verbose_name_plural = verbose_name
	def WorkSheet_id(self):
		return self.WorkSheet.Id
	WorkSheet_id.short_description  = '工单号'

	@property
	def day(self):
		return self.Check1.strftime("%Y-%m-%d")

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
	Cell = models.ForeignKey('Cell', on_delete=models.CASCADE, null=True,blank=True)
	WorkSheet = models.ForeignKey('WorkSheet' ,on_delete=models.CASCADE, null=True,blank=True, verbose_name = "工单号")
	DataTime = models.DateTimeField("时间"); 
	Pezzi = models.IntegerField("生产工件数");
	ReqPezzi = models.IntegerField("需求工件数");
	ResidPezzi = models.IntegerField("待生产工件数");
	PieceTime = models.IntegerField("单件加工时长");
	def __str__(self):
		return "pezz:" + self.DataTime.strftime("%Y-%m-%d") + "-" + str(self.Cell_id)
	class Meta:
		db_table = "[%s].[Pezzi]"% schema
		app_label = app_name
		verbose_name = '生产信息日志'
		verbose_name_plural = verbose_name
	def Cell__Plant(self):
		return self.Cell.Plant
	def Cell__Name(self):
		return self.Cell.Name
	def Cell__CellID(self):
		return self.Cell.CellID	
	def WorkSheet_id(self):
		return self.WorkSheet_id
	WorkSheet_id.short_description  = '工单号'
	Cell__Plant.short_description  = '车间'
	Cell__Name.short_description  = '机台'
	Cell__CellID.short_description  = '机台编号'
	@property
	def day(self):
		return self.DataTime.strftime("%Y-%m-%d")

class Stato(models.Model):
	"""工作状态切换日志"""
	Cell = models.ForeignKey('Cell', on_delete=models.CASCADE, null=True,blank=True)
	WorkSheet = models.ForeignKey('WorkSheet', on_delete=models.CASCADE, null=True,blank=True)
	DataTime = models.DateTimeField("时间"); 
	stato_choics =((0, "运行"),(1, "停止"),(2, "异常"),(3, "离线"))
	Stato = models.IntegerField("状态切换", choices= stato_choics);
	Alarmi = models.ForeignKey('Alarmi', on_delete=models.CASCADE, null=True,blank=True);
	TimeSpan = models.FloatField("时长-s", null=True, blank=True);
	def __str__(self):
		return "stato:" + self.DataTime.strftime("%Y-%m-%d") + "-" + str(self.Cell_id)
	class Meta:
		db_table = "[%s].[Stato]"% schema
		app_label = app_name
		verbose_name = '设备状态切换表'
		verbose_name_plural = verbose_name
	def Cell__Plant(self):
		return self.Cell.Plant
	def Cell__Name(self):
		return self.Cell.Name
	def Cell__CellID(self):
		return self.Cell.CellID
	def WorkSheetId(self):
		return self.WorkSheet_id
	WorkSheetId.short_description  = '工单号'
	Cell__Plant.short_description  = '车间'
	Cell__Name.short_description  = '机台'
	Cell__CellID.short_description  = '机台编号'
	@property
	def day(self):
		return self.DataTime.strftime("%Y-%m-%d")
		
class Cell(models.Model):
	id = models.IntegerField(primary_key=True );	
	stato_choics =((0, "运行"),(1, "停止"),(2, "异常"),(3, "离线"))
	type_choics = ((1, "新代系统"), (2, "PLC"))
	CellID = models.IntegerField("机台编号");
	Plant = models.CharField("车间", max_length=40);
	Name = models.CharField("机台", max_length=40);
	Type = models.IntegerField(verbose_name="系统", choices= type_choics)
	Stato = models.IntegerField(verbose_name="当前状态", choices= stato_choics) 
	IP = models.CharField("设备IP", max_length=20, blank=True);
	Create = models.DateTimeField("创建日期");
	OnLine = models.FloatField("在线时长");
	WorkTM = models.FloatField("作业时长");

	def status(self):
		return self.get_Stato_display()

	def OnLineStr(self):
		return sec2TmStr(self.OnLine)
	def WorkTMStr(self):
		return sec2TmStr(self.WorkTM)

	status.short_description = '当前状态'
	OnLineStr.short_description = '在线时长'
	WorkTMStr.short_description = '作业时长'
	def __str__(self):
		return self.Name + str(self.CellID) 
	class Meta:
		db_table = "[%s].[Cell]"% schema
		app_label = app_name
		verbose_name = '设备管理表'
		verbose_name_plural = verbose_name
	def combined_str(self):
		return ''.join([str(self.CellID), " ", self.Name])

class Record(models.Model):
	Cell = models.ForeignKey('Cell', on_delete=models.CASCADE, null=True,blank=True)
	WorkSheet = models.ForeignKey('WorkSheet', on_delete=models.CASCADE, null=True,blank=True)
	StartTime = models.DateTimeField("开始时间"); 
	StopTime = models.DateTimeField("结束时间",null=True, max_length =20);
	Status = models.CharField(null=True, max_length =20); 
	Mode = models.CharField("工作模式",null=True, max_length =20); 
	FinishParts = models.IntegerField("完成工件数",null=True, blank=True);
	IdleTMSec = models.FloatField();
	PowerOnSec = models.FloatField();
	WorkingSec = models.FloatField();
	EstimatedSec = models.FloatField(null=True, blank=True);

	def __str__(self):
		return "Record:" + self.StartTime__date + "-" + self.WorkSheet_id
	class Meta:
		db_table = "[%s].[Record]"% schema
		app_label = app_name
		verbose_name = '工单加工日志'
		verbose_name_plural = verbose_name		
	def WorkSheet_id(self):
		return self.WorkSheet.Id
	WorkSheet_id.short_description  = '工单号'

class RecordManage(Record):
	class Meta:
		proxy = True
		app_label = app_name
		verbose_name = '工单加工记录'
		verbose_name_plural = verbose_name

class WorkSheet(models.Model):
	"""订单表"""
	Id = models.CharField("工单号", max_length =50, primary_key=True );	
	Cell = models.ForeignKey('Cell', on_delete=models.CASCADE, null=True,blank=True)
	Order = models.ForeignKey('Order', on_delete=models.CASCADE, null=True,blank=True, verbose_name = '订单号')
	Product_id = models.CharField("款号", max_length =50); 
	Status = models.CharField("工单状态",null=True, max_length =20, editable=False); 
	ProcessID = models.CharField("工序备注",null=True, max_length =50); 
	FinishParts = models.IntegerField("完成工件数",null=True, blank=True, editable=False); 
	ReqParts = models.IntegerField("需求工件数",null=True, blank=True, editable=False); 	
	AddReqParts = models.IntegerField("追加工件数",null=True, blank=True, editable=False); 
	def __str__(self):
		return self.Id
	class Meta:
		db_table = "[%s].[WorkSheet]"% schema
		app_label = app_name
		verbose_name = '工单管理表'
		verbose_name_plural = verbose_name
	def Cell__Plant(self):
		return self.Cell.Plant
	def Cell__Name(self):
		return self.Cell.Name
	def Cell__CellID(self):
		return self.Cell.CellID
	def Order_id(self):
		return self.Order.Id
	Order_id.short_description  = '订单号'
	Cell__Plant.short_description  = '车间'
	Cell__Name.short_description  = '机台'
	Cell__CellID.short_description  = '机台编号'

class Order(models.Model):
	"""订单表"""
	Id = models.CharField("订单号",max_length =50 ); 
	Status = models.CharField("订单状态",null=True, max_length =20, editable=False); 
	Colour = models.CharField("产品颜色",null=True, max_length =50);
	Product_id = models.CharField("产品款号",null=True, max_length =50); 
	ReqParts = models.IntegerField("需求工件数",null=True, blank=True, editable=False); 	
	def __str__(self):
		return self.Id
	class Meta:
		db_table = "[%s].[Order]"% schema
		app_label = app_name
		verbose_name = '订单管理表'
		verbose_name_plural = verbose_name
    