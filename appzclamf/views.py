from django.shortcuts import render, redirect
#Create your views here.
from django.db.models import Q
from appzclamf.models import  Alarm, Pezzi, Stato, LiveStats

import datetime

def getAlarmStr(alarmID):
    ser_q = Alarm.objects.filter(Q(AllarmID__get = alarmID))
    return ser_q[0].AllarmString

def login(req):
    if req.method == 'GET':        
        return render(req, "login.html", {"Title":'login'});
    user = req.POST.get("user");
    pwd = req.POST.get("password");
    if (not(user) or not(pwd)):
        return render(req, "login.html", {"errmsg":u'用户名或密码不正确！'});
    userdic = {id:user, pwd:pwd}
    return redirect("/inex/");

def index(req):
    q_cellaDic = LiveStats.objects.values("CellaID").distinct()
    return render(req, "index.html", {"Title":"index", "cellIDQ":q_cellaDic});

def alarm(req):
    q_cellaDic = LiveStats.objects.values("CellaID").distinct()
    queryset = Alarm.objects.all()
    return render(req, "alarm.html", {"Title":"alarm","cellIDQ":q_cellaDic, "queryset":queryset})

def livestats(req):
    q_cellaDic = LiveStats.objects.values("CellaID").distinct()
    cellsLiveStatus = []
    for i in range(len(q_cellaDic)):
        cellaID = q_cellaDic[i]["CellaID"];
        celldic = {"CellaID": cellaID}
        celldic['LiveCheckQ'] = LiveStats.objects.order_by('-id').filter( CellaID=cellaID)
        cellsLiveStatus.append(celldic)
    return render(req, "livestats.html", {"Title":"livestats", "cellIDQ":q_cellaDic,  "queryset":cellsLiveStatus});

def pezzi(req):
    q_cellaDic = LiveStats.objects.values("CellaID").distinct()

    if req.method == 'GET': 
        cellaID = q_cellaDic[0]["CellaID"];
    else:
        cellaID = req.POST.get("cellID");
    curr_time = datetime.datetime.now().strftime("%Y/%m/%d") 
    #queryset = Pezzi.objects.filter(Q(CellaID__get = cellID)&Q( Data__get=curr_time))
    queryset = Pezzi.objects.filter( CellaID=cellaID)#.filter( Data=curr_time)
    #return render(req, "pezzi.html", {"Title":(len(q_cellaDic))})

    return render(req, "pezzi.html", {"Title":"pezzi","cellIDQ":q_cellaDic, "cellID":cellaID,  "queryset":queryset})

def stato(req):
    q_cellaDic = LiveStats.objects.values("CellaID").distinct()

    if req.method == 'GET': 
        cellaID = q_cellaDic[0]["CellaID"];
    else:
        cellaID = req.POST.get("cellID");
    queryset = Stato.objects.filter( CellaID=cellaID)
    return render(req, "stato.html", {"Title":"stato", "cellIDQ":q_cellaDic, "cellID":cellaID,  "queryset":queryset})
