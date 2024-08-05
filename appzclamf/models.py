from django.db import models

schema = "CNC700Cutting"
class Alarmi(models.Model):
	""""告警索引表"""
	#Id = models.IntegerField();
	AllarmID = models.SmallIntegerField()
	AllarmString = models.CharField(max_length=50, null=True, blank=True)
	TypeID = models.IntegerField(null=True, blank=True)
	Description_Id = models.IntegerField(null=True, blank=True)
	class Meta:
		db_table = "[%s].[Alarmi]"% schema

class LiveState(models.Model):
	"""在线日志"""
	#Id = models.IntegerField();
	CellaID = models.IntegerField(null=True, blank=True);
	Plant = models.CharField(max_length=50,  blank=True);
	Check1 = models.DateTimeField(null=True, blank=True);
	Check2 =  models.DateTimeField(null=True, blank=True);
	Note_Id = models.CharField(max_length=50, blank=True);
	class Meta:
		db_table = "[%s].[LiveState]"% schema

class Pezzi(models.Model):
	"""产量信息日志"""
	#Id = models.IntegerField();
	CellaID = models.IntegerField(null=True, blank=True);
	Plant = models.CharField(null=True,max_length=50);
	OrderID = models.CharField(null=True, max_length =50);
	DataTime = models.CharField(null=True, max_length =50); 
	Pezzi = models.IntegerField(null=True, blank=True);
	ReqPezzi = models.IntegerField(null=True, blank=True);
	ResidPezzi = models.IntegerField(null=True, blank=True);
	PieceTime = models.IntegerField(null=True, blank=True);
	EstimatedTm = models.CharField(null=True, max_length=50);
	TotWorkTm = models.CharField(null=True, max_length=50);
	class Meta:
		db_table = "[%s].[Pezzi]"% schema

class Stato(models.Model):
	"""工作状态切换日志"""
	#Id = models.IntegerField();
	CellaID = models.IntegerField(null=True, blank=True);
	Plant = models.CharField(max_length=50);
	OrderID = models.CharField(null=True, max_length =50); 
	DataTime = models.CharField(null=True, max_length =50); 
	stato_choics =(
		(True, "运行"),
		(False, "停止")
	)
	Stato = models.BooleanField(null=True, blank=True, choices= stato_choics);
	Alarm = models.IntegerField(null=True, blank=True);
	class Meta:
		db_table = "[%s].[Stato]"% schema

class Order(models.Model):
	"""订单表"""
	#Id = models.IntegerField();
	CellaID = models.IntegerField(null=True, blank=True);
	Plant = models.CharField(max_length=50);
	OrderID = models.CharField(null=True, max_length =50); 
	WorkStatus = models.CharField(null=True, max_length =50); 
	StytleNum = models.CharField(null=True, max_length =50); 
	FinishParts = models.CharField(null=True, max_length =50); 
	RequireParts = models.CharField(null=True, max_length =50); 
	class Meta:
		db_table = "[%s].[Order]"% schema

class OrderHistory(models.Model):
	#Id = models.IntegerField();
	CellaID = models.IntegerField(null=True, blank=True);
	Plant = models.CharField(max_length=50);
	OrderID = models.CharField(null=True, max_length =50); 
	StartTime = models.CharField(null=True, max_length =50); 
	StopTime = models.CharField(null=True, max_length =50); 
	Status = models.CharField(null=True, max_length =50); 
	Mode = models.CharField(null=True, max_length =50); 
	PowerOnTM = models.CharField(null=True, max_length =50); 
	WorkingTM = models.CharField(null=True, max_length =50); 
	FinishParts = models.CharField(null=True, max_length =50); 
	class Meta:
		db_table = "[%s].[OrderHistory]"% schema