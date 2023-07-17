from django.db import models

#Create your models here.

# class Base (models.Model):
#     m2m = models.ManyToManyField (
#         "AutoSheet1" ,
#         related_name = "  %(class)s _related" ,
#         related_query_name = " %(class)s s" ,
#     )
#     class Meta :
#         abstract = True
#         db_table = "%(class)s"

class Alarm(models.Model):
	""""告警索引表"""
	#Id = models.IntegerField();
	AllarmID = models.SmallIntegerField()
	AllarmString = models.CharField(max_length=50, null=True, blank=True)
	TypeID = models.IntegerField(null=True, blank=True)
	Description_Id = models.IntegerField(null=True, blank=True)
	class Meta:
		db_table = "[zclDb].[Alarmi]"
	# def _str_(self):
	# 	return "%d : %s :%d: %d"%(self.AllarmID, self.AllarmString, self.TypeID, self.Description_Id)

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
		db_table = "[zclDb].[Event]"

class LiveStats(models.Model):
	"""在线日志"""
	#Id = models.IntegerField();
	Plant = models.CharField(max_length=50,  blank=True);
	CellaID = models.IntegerField(null=True, blank=True);
	Check1 = models.DateTimeField(null=True, blank=True);
	Check2 =  models.DateTimeField(null=True, blank=True);
	Note_Id = models.IntegerField(null=True, blank=True);
	class Meta:
		db_table = "[zclDb].[LiveState]"

class Message(models.Model):
	"""消息ID索引表"""
	#Id = models.IntegerField();
	MessageID = models.IntegerField();
	MessageString = models.CharField(null=True, max_length=4000);
	Description_Id = models.IntegerField(null=True, blank=True);
	class Meta:
		db_table = "[zclDb].[Messaggi]"

class Pezzi(models.Model):
	"""产量信息日志"""
	EventID = models.IntegerField(primary_key=True);
	Data = models.CharField(null=True, max_length=100); #date
	Plant = models.CharField(null=True,max_length=50);
	CellaID = models.IntegerField(null=True, blank=True);
	MainProg = models.CharField(null=True, max_length=100);
	Pezzi = models.IntegerField(null=True, blank=True);
	Ora = models.CharField(null=True, max_length=100);
	JobMode = models.CharField(null=True, max_length=50);
	class Meta:
		db_table = "[zclDb].[Pezzi]"

class Stato(models.Model):
	"""工作状态切换日志"""
	StatoID = models.IntegerField(primary_key=True);
	Data = models.CharField(max_length=100); #date
	Ora = models.CharField(max_length=100); #time(2);
	Plant = models.CharField(max_length=50);
	CellaID = models.IntegerField(null=True, blank=True);
	stato_choics =(
		(1, "运行"),
		(0, "停止")
	)
	Stato = models.BooleanField(null=True, blank=True, choices= stato_choics);
	Alarm = models.IntegerField(null=True, blank=True);
	class Meta:
		db_table = "[zclDb].[Stato]"

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
		db_table = "[zclDb].[Incoming]"

