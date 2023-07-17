from django.shortcuts import render, redirect

#Create your views here.
from appzclamf.models import  Alarm, Pezzi, Stato, LiveStats

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
    return render(req, "index.html");

def alarm(req):
    queryset = Alarm.objects.all()
    return render(req, "alarm.html", {"Title":"alarm", "queryset":queryset})

def livestats(req):
    queryset = LiveStats.objects.all().ordered(-id)
    return render(req, "livestats.html", {"Title":"LiveStats", "queryset":queryset})

def pezzi(req):
    q_cellaID = Pezzi.objects.values("CellaID").distinct()
    print (len(q_cellaID))
    if req.method == 'GET': 
        cellID = q_cellaID[0].CellaID
    else:
        cellID = req.POST.get("cellID");
    queryset = Pezzi.objects.filter(CellaID = cellID).ordered(-id)
    return render(req, "pezzi.html", {"Title":(len(q_cellaID))})
    #return render(req, "pezzi.html", {"Title":"pezzi", "cellID":cellID,"cellIDQ":q_cellaID,  "queryset":queryset})

def stato(req):
    queryset = Stato.objects.all().ordered(-id)
    return render(req, "stato.html", {"Title":"stato", "queryset":queryset})
