from django.shortcuts import render, redirect
#Create your views here.
from django.db.models import Q
from appzclamf.models import  Alarmi, Pezzi, Stato, LiveState

from datetime import datetime, timezone, timedelta, date, time
from plotly.offline import plot
from plotly.graph_objs import Scatter
import appzclamf.api.dbFilter as mydb
import pytz
tz = pytz.timezone('Asia/Shanghai')

colorList = ['red', 'green', 'orange', 'purple', 'brown', 'plum', 'yellow']
def getAlarmStr(alarmID):
    ser_q = Alarmi.objects.filter(Q(AllarmID__get = alarmID))
    return ser_q[0].AllarmString

def getCellLiveStats(cellID):
    l_liveStatses = LiveState.objects.order_by('-id').filter( CellaID=cellID)
    return l_liveStatses

def getCellPezzi(cellID):
    l_Pezzi = Pezzi.objects.filter( CellaID=cellID).order_by('-EventID')
    return l_Pezzi

def getCellStato(cellID):
    l_Stato = Stato.objects.filter( CellaID=cellID).order_by('-StatoID')
    return l_Stato

def getCellQ(isGetTmD = False):
    l_CelleQ = LiveState.objects.values("CellaID").distinct()
    l_Celle = []
    for i in range(len(l_CelleQ)):
        dic = {"CellaID": l_CelleQ[i]["CellaID"]}
        dic["IsOnline"] = getLastCheck1(l_CelleQ[i]["CellaID"])
        dic["checktimeList"],dic["totOnlineTm"],dic["totWorkTm"],dic["totOnlineday"] = getCheckTime(l_CelleQ[i]["CellaID"], isGetTmD)
        dic['color'] = colorList[i]
        l_Celle.append(dic)
    return l_Celle

def getLastCheck1(cellID):
    curr_time = datetime.now(tz) + timedelta(minutes=-5)
    curr_time = curr_time.replace(tzinfo=None)
    l_lastCheck1 = LiveState.objects.filter( CellaID=cellID).values("Check1", "Check2").last()
    isOnline =  curr_time < l_lastCheck1['Check1']
    return isOnline
def getCheckTime(cellID, isGetTmD):
    checktimeList = []
    totOnlineTm = 0
    totWorkTm = 0
    totOnlineday = 0
    if not(isGetTmD):
        return checktimeList, totOnlineTm, totWorkTm, totOnlineday;
    checkList = LiveState.objects.order_by('-id').filter( CellaID=cellID).values("Check1", "Check2")
    for i in range(len(checkList)):
        check1 = checkList[i]['Check1']
        check1 = check1.replace(tzinfo=None)
        if i < len(checkList)-1 :
            check2 = checkList[i+1]['Check2']
            check2 = check2.replace(tzinfo=None)
        else:
            check2 = datetime.combine(check1.date(),datetime.min.time()) +  timedelta(hours= 8)
        day = check2.date().strftime("%Y/%m/%d")
        lastId = len(checktimeList) - 1
        oldday = 0 if i==0 else checktimeList[lastId]['day']
        onlinetime = round((check1-check2)/timedelta(hours= 1),2)
        if (oldday != day):
            onlineDic = {'day': day, 'start' : check2, 'stop' : check1}
            onlineDic['timeline'] = onlinetime
            onlineDic['worktime'], onlineDic['abnorm'] = getWorkTime(cellID, onlineDic["day"], onlineDic["stop"], onlineDic["start"])
            onlineDic['idleTm'] = round(onlineDic['timeline'] - onlineDic['worktime'],2)
            checktimeList.append(onlineDic)
            totOnlineday = totOnlineday + 1
            totOnlineTm = totOnlineTm + onlinetime
            totWorkTm = totWorkTm + onlineDic['worktime']
        else:
            totWorkTm = totWorkTm - checktimeList[lastId]['worktime']
            checktimeList[lastId]['start'] = check2
            checktimeList[lastId]['timeline'] = round(checktimeList[lastId]['timeline'] + onlinetime,2)
            checktimeList[lastId]['worktime'], checktimeList[lastId]['abnorm'] = getWorkTime(cellID, onlineDic["day"], onlineDic["stop"], onlineDic["start"])
            checktimeList[lastId]['idleTm'] = round(checktimeList[lastId]['timeline'] - checktimeList[lastId]['worktime'],2)
            totOnlineTm = totOnlineTm + onlinetime
            totWorkTm = totWorkTm + checktimeList[lastId]['worktime']
    return checktimeList, totOnlineTm, totWorkTm, totOnlineday

def strToDate(datestr):
    return date(*map(int, datestr.split("/")))

def strToTime(timestr):
    return time(*map(int, timestr.split(".")[0].split(":")))

def combineDatetime(data):
    return datetime.combine(strToDate(data['Data']), strToTime(data['Ora']))

def getWorkTime(cellID, day, check1, check2):
    statoList = Stato.objects.filter(CellaID=cellID, Data=day).values("Data", "Ora","Stato",'Alarm')
    if(len(statoList) < 1):
        theStart = Stato.objects.filter(CellaID=cellID).values("Data", "Ora","Stato",'Alarm').last()
        if theStart['Stato']: 
            return round((check1-check2)/timedelta(hours= 1),2), 0
        else:
            return 0, 0
    end = len(statoList)-1
    abnomalTm = timedelta(seconds = 0)
    if statoList[end]['Stato']:
        worktime = check1
    else:
        worktime = combineDatetime(statoList[end])
        if (statoList[end]['Alarm']>0):
            abnomalTm = check1 - worktime
        end = end -1
    for i in range(end,-1,-1):
        time = combineDatetime(statoList[i])
        if statoList[i]['Stato'] and (isinstance(worktime, datetime)):
            worktime = worktime - time
        elif not(statoList[i]['Stato']):
            worktime = time + worktime
            if (statoList[i]['Alarm']>0):
                abnomalTm = combineDatetime(statoList[i+1]) + abnomalTm - time
    if not(statoList[0]['Stato']):
        worktime = worktime-check2 
    return round(worktime/timedelta(hours= 1),2),  round(abnomalTm/timedelta(hours= 1),2)
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
    #day = datetime.now(tz).strftime('%Y-%m-%d')
    q_cellaDic = mydb.getDataForIndex("")
    return render(req, "index.html", {"Title":"index", "cellIDQList":q_cellaDic});

def alarm(req):
    q_cellaDic = getCellQ()
    queryset = Alarmi.objects.all()
    return render(req, "Alarmihtml", {"Title":"alarm","cellIDQ":q_cellaDic, "queryset":queryset})

def livestats(req):
    q_cellaDic = getCellQ()
    if req.method == 'GET': 
        cellaID = q_cellaDic[0]["CellaID"];
    elif req.method == 'POST':
        cellaID =req.POST.get("cellID");
    queryset = getCellLiveStats(cellaID)
    return render(req, "LiveState.html", {"Title":"livestats", "cellIDQ":q_cellaDic, "cellID":cellaID, "queryset":queryset});

def pezzi(req):
    q_cellaDic = getCellQ()
    if req.method == 'GET': 
        cellaID = q_cellaDic[0]["CellaID"];
    elif req.method == 'POST':
        cellaID = req.POST.get("cellID");
    queryset = getCellPezzi(cellaID)#.filter( Data=curr_time)
    return render(req, "pezzi.html", {"Title":"pezzi","cellIDQ":q_cellaDic, "cellID":cellaID,  "queryset":queryset})

def stato(req):
    q_cellaDic = getCellQ()
    if req.method == 'GET': 
        cellaID = q_cellaDic[0]["CellaID"];
    elif req.method == 'POST':
        cellaID = req.POST.get("cellID");
    queryset = getCellStato(cellaID)
    return render(req, "stato.html", {"Title":"stato", "cellIDQ":q_cellaDic, "cellID":cellaID,  "queryset":queryset})

def building(req):
    q_cellaDic = getCellQ(True)
    return render(req, "building.html", {"Title":"建设中", "cellIDQ":q_cellaDic});

def livestats_detal(req):
    q_cellaDic = getCellQ(True)
    dataList =[]
    t_x_data = []
    t_y_data = []
    for cellaDic in q_cellaDic:
        x_data = [obj['day'] for obj in cellaDic["checktimeList"]]
        y_data = [obj['timeline'] for obj in cellaDic["checktimeList"]]

        data = Scatter(x=x_data[::-1],y=y_data[::-1], mode='lines',name=str(cellaDic['CellaID'])+' # 设备在线趋势',opacity=0.8,marker_color=cellaDic['color'])
        dataList.append(data)
    plot_div = plot(dataList,output_type='div')
    context = {'plot_div':plot_div, "cellIDQ":q_cellaDic}
    return render(req,'test.html',context=context)

def test(req):
    q_cellaDic = mydb.getCellDic()
    dataList =[]
    t_x_data = []
    t_y_data = []
    for cellaDic in q_cellaDic:
        x_data = [obj['day'] for obj in cellaDic["tms"]]
        y_data = [obj['onlineTm'] for obj in cellaDic["tms"]]

        data = Scatter(x=x_data[::-1],y=y_data[::-1], mode='lines',name=str(cellaDic['CellaID'])+' # 设备在线趋势',opacity=0.8,marker_color=cellaDic['color'])
        dataList.append(data)
    plot_div = plot(dataList,output_type='div')
    context = {'plot_div':plot_div, "cellIDQ":q_cellaDic}
    return render(req,'test1.html',context=context)

def listOrder(req):
    queryset = mydb.getOrderList()
    return render(req, "orderList.html", {"Title":"listOrder", "queryset":queryset});

