from django.db import models

schema = "AutoSheet1"
class Alarm(models.Model):
	""""告警索引表"""
	#Id = models.IntegerField();
	AllarmID = models.SmallIntegerField()
	AllarmString = models.CharField(max_length=50, null=True, blank=True)
	TypeID = models.IntegerField(null=True, blank=True)
	Description_Id = models.IntegerField(null=True, blank=True)
	class Meta:
		db_table = "[%s].[Alarmi]"% schema
		#db_table = "[AutoSheet1].[Alarmi]"

class Event(models.Model):
	"""事件日志"""
	EventID = models.IntegerField(primary_key= True);
	Data = models.CharField(max_length=100); #date
	Ora = models.CharField(max_length=100); #time(2);
	Plant = models.CharField(null=True,max_length=50);
	CellaID = models.IntegerField(null=True, blank=True);
	Microlotto = models.IntegerField(null=True, blank=True);
	Modello =  models.CharField(null=True,max_length=50);
	Calibro = models.IntegerField(null=True, blank=True);
	Colore = models.CharField(null=True, max_length=50);
	Pezzi = models.IntegerField(null=True, blank=True);
	Evento = models.IntegerField(null=True, blank=True);
	class Meta:
		db_table = "[%s].[Event]"% schema

class LiveStats(models.Model):
	"""在线日志"""
	#Id = models.IntegerField();
	Plant = models.CharField(max_length=50,  blank=True);
	CellaID = models.IntegerField(null=True, blank=True);
	Check1 = models.DateTimeField(null=True, blank=True);
	Check2 =  models.DateTimeField(null=True, blank=True);
	Note_Id = models.IntegerField(null=True, blank=True);
	class Meta:
		db_table = "[%s].[LiveState]"% schema

class Message(models.Model):
	"""消息ID索引表"""
	#Id = models.IntegerField();
	MessageID = models.IntegerField();
	MessageString = models.CharField(null=True, max_length=4000);
	Description_Id = models.IntegerField(null=True, blank=True);
	# class Meta:
	class Meta:
		db_table = "[%s].[Messaggi]"% schema

class Pezzi(models.Model):
	"""产量信息日志"""
	EventID = models.IntegerField(primary_key=True);
	Data = models.CharField(null=True, max_length =100); #date
	Plant = models.CharField(null=True,max_length=50);
	CellaID = models.IntegerField(null=True, blank=True);
	MainProg = models.CharField(null=True, max_length=100);
	Pezzi = models.IntegerField(null=True, blank=True);
	Ora = models.CharField(null=True, max_length=100);
	JobMode = models.CharField(null=True, max_length=50);
	class Meta:
		db_table = "[%s].[Pezzi]"% schema

class Stato(models.Model):
	"""工作状态切换日志"""
	StatoID = models.IntegerField(primary_key=True);
	Data = models.CharField(max_length=100); #date
	Ora = models.CharField(max_length=100); #time(2);
	Plant = models.CharField(max_length=50);
	CellaID = models.IntegerField(null=True, blank=True);
	stato_choics =(
		(True, "运行"),
		(False, "停止")
	)
	Stato = models.BooleanField(null=True, blank=True, choices= stato_choics);
	Alarm = models.IntegerField(null=True, blank=True);
	class Meta:
		db_table = "[%s].[Stato]"% schema

class Incoming(models.Model):
	"""订单表"""
	ordernumber = models.IntegerField(primary_key=True);
	type = models.CharField(max_length=10, null=True);
	year = models.CharField(max_length=10, null=True);
	model = models.CharField(max_length=20, null=True);
	cal = models.CharField(max_length=10, null=True);
	color = models.CharField(max_length=10, null=True);
	material = models.CharField(max_length=10, null=True);
	quantity = models.CharField(max_length=10, null=True);
	class Meta:
		db_table = "[%s].[Incoming]"% schema

