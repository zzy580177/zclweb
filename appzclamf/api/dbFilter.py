from django.db.models import Q
import numpy as np
from appzclamf.models import  Alarm, Pezzi, Stato, LiveStats
from datetime import datetime, timezone, timedelta, date, time
import pandas as pd

np_dtype = "datetime64[us]"

def getAlarmStr(alarmID):
    ser_q = Alarm.objects.filter(Q(AllarmID__get = alarmID))
    return ser_q[0].AllarmString

def getCellLives(cellID):
    ser_q = LiveStats.objects.order_by("-id").filter( CellaID=cellID)
    return ser_q

def getCellPezzis(cellID):
    ser_q = Pezzi.objects.filter( CellaID=cellID).order_by("-EventID")
    return ser_q

def getCellStatos(cellID):
    ser_q = Stato.objects.filter( CellaID=cellID).order_by("-StatoID")
    return ser_q

def getOnLinsDates(cellID):
    ser_q = Stato.objects.filter( CellaID=cellID).order_by("-StatoID").values_list("Data", flat=True)
    date_v = [data for data in ser_q]
    date_v = pd.Series(date_v).drop_duplicates().tolist()
    return date_v

def isCellOnline(cellID ,time):
    return getCellLives(cellID).filter(Check1__gt=time).exists()

def isStatosExitsByDay(cellID, day):
    result = getCellStatos(cellID).filter(Data = day).exists()
    return result

def isStatosExitsByTime(cellID, day, time, alarm_v):
    result = getCellStatos(cellID).filter(Data = day, Ora__gt=time, Stato = False, Alarm = alarm_v).exists()
    return result

def getCheck1List(cellID, start, stop):
    ser_q = LiveStats.objects.order_by("-id").filter(CellaID=cellID, Check1__range=(start, stop)).values_list("Check1")
    date_v = [data for data in ser_q]
    return np.array(date_v, dtype= np_dtype)

def getCheck2List(cellID, start, stop):
    ser_q = LiveStats.objects.order_by("-id").filter(CellaID=cellID, Check2__range=(start, stop)).values_list("Check2")
    date_v = [data for data in ser_q]
    return np.array(date_v, dtype= np_dtype)

def getCellOnlineTimeByDay(cellID, day):
    start, stop = generateTmFilerRange(day)
    check1 = getCheck1List(cellID, start, stop)
    check2 = getCheck2List(cellID, start, stop)
    df_sum = timedelta(seconds = 0)
    if (check1.size > check2.size):
        check2 = np.append(check2, [np.datetime64(start)])
    if (check1.size == check2.size):
        df_sum = np.subtract(check1,check2).sum()
    if df_sum > timedelta(seconds = 0):
        return df_sum.astype("timedelta64[s]").astype(int)
    else:
        return 0

def getCellPezzisByDay(cellID, day):
    ser_q = getCellPezzis(cellID).filter(Data = day).values("Pezzi","ReqPezzi", "TotPezzi").first()
    return ser_q

def isPezzisExitsByDay(cellID, day):
    result = getCellPezzis(cellID).filter(Data = day).exists()
    return result

def strToDate(datestr):
    return date(*map(int, datestr.split("-")))

def strToTime(timestr):
    return time(*map(int, timestr.split(".")[0].split(":")))

def datetimeCom(date,time):
    return datetime.combine(strToDate(date), time)

def generateTmFilerRange(day):
    start = datetimeCom(day, datetime.min.time())
    stop = start + timedelta(hours= 24)
    curr_time = datetime.now()
    stop = stop if stop < curr_time else curr_time
    return start, stop

def getStartTmList(cellID, day):
    ora_q = getCellStatos(cellID).filter(Data = day, Stato = False).values_list("Ora", flat=True)
    date_v = [data for data in ora_q]
    for i in range(len(date_v)):
        date_v[i] = datetimeCom(day,strToTime(date_v[i]))
    return np.array(date_v , dtype= np_dtype)

def getStopTmList(cellID, day):
    ora_q = getCellStatos(cellID).filter(Data = day, Stato = False).values_list("Ora", flat=True)
    date_v = [data for data in ora_q]
    for i in range(len(date_v)):
        date_v[i] = datetimeCom(day,strToTime(date_v[i]))
    return np.array(date_v, dtype= np_dtype)

def getWorkTmsum(stopTms, startTms, day):
    start, stop = generateTmFilerRange(day)
    if ( startTms.size > stopTms.size):
        stopTms = np.insert(stopTms,0,[np.datetime64(stop)])
    if ( startTms.size < stopTms.size):
        startTms = np.append(startTms, [np.datetime64(start)])
    if ( startTms.size == stopTms.size):
        sum = np.subtract(stopTms,startTms).sum()
        return sum.astype("timedelta64[s]").astype(int)
    else:
        return 0

def getIdleTmsum(stopTms, startTms, day):
    start, stop = generateTmFilerRange(day)
    if ( startTms.size > stopTms.size):
        stopTms = np.append(stopTms, [np.datetime64(start)])
    if ( startTms.size < stopTms.size):
        startTms = np.insert(startTms,0,[np.datetime64(stop)])
    if ( startTms.size == stopTms.size):
        sum = np.subtract(startTms,stopTms).sum()
        return sum.astype("timedelta64[s]").astype(int)
    else:
        return 0

colorList = ["red", "green", "orange", "purple", "brown", "plum", "yellow"]

def getCellQ():
    q_set = LiveStats.objects.values("CellaID").distinct()
    l_Celle = []
    l_CelleQ = [livestats for livestats in q_set]
    for i in range(len(l_CelleQ)):
        cellID = l_CelleQ[i]["CellaID"]
        dic = {"CellaID": cellID, "onlineTms" :[], "workTms":[], "abnormTms":[], "ildetms" : []}
        dic["IsOnline"] = isCellOnline(cellID)
        dic["color"] = colorList[i]
        dic["days"] = getOnLinsDates(cellID)
        for i in range(len(dic["days"])):
            start, stop = generateTmFilerRange(dic["days"][i])
            dic["onlineTms"].append(getCellOnlineTimeByDay(cellID, dic["days"][i]))
            stopTms = getStopTmList(cellID, datetime.now().strftime("%Y-%m-%d"))
            startTms = getStartTmList(cellID, datetime.now().strftime("%Y-%m-%d"))
            dic["workTms"].append(getWorkTmsum(stopTms, startTms, start, stop))
            dic["ildetms"].append(getIdleTmsum(stopTms, startTms, start, stop))
            dic["abnormTms"].append(0)
        l_Celle.append(dic)
    return l_Celle

def getCellDic():
    q_set = LiveStats.objects.values("CellaID").distinct()
    l_Celle = []
    l_CelleQ = [livestats for livestats in q_set]
    for i in range(len(l_CelleQ)):
        cellID = l_CelleQ[i]["CellaID"]
        dic = {"CellaID": cellID, "tms" :[]}
        dic["IsOnline"] = isCellOnline(cellID)
        dic["color"] = colorList[i]
        dic["days"] = getOnLinsDates(cellID)
        for i in range(len(dic["days"])):
            tmdic = {}
            start, stop = generateTmFilerRange(dic["days"][i])
            stopTms = getStopTmList(cellID, datetime.now().strftime("%Y-%m-%d"))
            startTms = getStartTmList(cellID, datetime.now().strftime("%Y-%m-%d"))
            tmdic["onlineTm"] = getCellOnlineTimeByDay(cellID, dic["days"][i])
            tmdic["workTm"] = getWorkTmsum(stopTms, startTms, start, stop)
            tmdic["ildeTm"] = getIdleTmsum(stopTms, startTms, start, stop)
            tmdic["abnormTm"] = 0
            tmdic["day"] = dic["days"][i]
            dic["tms"].append(tmdic)
        l_Celle.append(dic)
    return l_Celle

def convert_to_hhmmss(td_array):
    m, s = divmod(td_array, 60)
    h, m = divmod(m, 60)
    time_for_hms = "%02d:%02d:%02d" % (h, m, s)
    return time_for_hms

def getCellPezziDic(day):
    q_set = LiveStats.objects.values_list("CellaID", flat=True).distinct()
    celleList = [livestats for livestats in q_set]
    output = []
    for i in range(len(celleList)):
        cellID = celleList[i]
        cell_dic = {"CellaID": cellID, "Note_Id":"精雕机"}
        cell_dic["ProcDic"] = getProcDic(cellID, day)
        cell_dic["PezzDic"] = getPezzDic(cellID, day)
        cell_dic["StatoDic"] = getCellCurrStatus(cellID)
        output.append(cell_dic)
    return output

def getProcDic(cellID, day):
    output={"WorkTm":0, "IldeTm":0, "AbnormTm": 0}
    output["OnlineTm"] = convert_to_hhmmss(getCellOnlineTimeByDay(cellID, day))
    if isStatosExitsByDay(cellID, day):
        stopTms = getStopTmList(cellID, day)
        startTms = getStartTmList(cellID, day)
        output["WorkTm"] = convert_to_hhmmss(getWorkTmsum(stopTms, startTms, day))
        output["IldeTm"] = convert_to_hhmmss(getIdleTmsum(stopTms, startTms, day))
    return output

def getCellCurrStatus(cellID):
    output = {"AlarmSrt":"无", "Status":"运行中"}
    curr_time = datetime.now(timezone.utc) + timedelta(minutes=-5)
    day = curr_time.strftime("%Y-%m-%d")
    time = curr_time.strftime("%H:%M:%S.%f")
    if (not isCellOnline(cellID, curr_time)):
        output["Status"] = "离线中"
    elif(isStatosExitsByTime(cellID, day, time, 0)):
        output["Status"] = "待机中"
    elif(isStatosExitsByTime(cellID, day, time, 1)):
        output["Status"] = "告警中" 
        #output["AlarmSrt"] = getAlarmStr[lastStato["Alarm"]]
    return output

def getPezzDic(cellID, day):
    output = {"Pezzi":"0","ReqPezzi":"0", "TotPezzi":"0", "Reach":"56"}
    if not(isPezzisExitsByDay(cellID, day)):
        return output
    pezz_q = getCellPezzisByDay(cellID, day)
    output["Pezzi"] = pezz_q["Pezzi"]
    output["ReqPezzi"] = pezz_q["ReqPezzi"]
    output["TotPezzi"] = pezz_q["TotPezzi"]  
    output["Reach"] = round((output["Pezzi"]*100/output["TotPezzi"]) )if output["TotPezzi"] >0 else 100
    return output

