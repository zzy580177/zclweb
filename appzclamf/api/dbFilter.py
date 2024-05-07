from django.db.models import Q
import numpy as np
from appzclamf.models import  Alarm, Pezzi, Stato, LiveStats
from datetime import datetime, timedelta, date, time
import pandas as pd

np_dtype = "datetime64[us]"
startTm = datetime.min.time()

def get_serq_Live(cellID):
    ser_q = LiveStats.objects.order_by("-id").filter( CellaID=cellID)
    return ser_q

def get_serq_pezzi(cellID):
    ser_q = Pezzi.objects.filter( CellaID=cellID).order_by("-EventID")
    return ser_q

def get_serq_stato(cellID):
    ser_q = Stato.objects.filter( CellaID=cellID).order_by("-StatoID")
    return ser_q

def get_value_AlarmStr(alarmID):
    ser_q = Alarm.objects.filter(Q(AllarmID__get = alarmID))
    return ser_q[0].AllarmString

def get_value_dailyPezzi(cellID, day):
    date_v = Pezzi.objects.filter( CellaID=cellID, Data = day).values_list("EventID","Pezzi","ReqPezzi","TotPezzi").last()
    return date_v

def get_valueList_check1(cellID, start, stop):
    ser_q = LiveStats.objects.filter(CellaID=cellID, Check1__range=(start, stop)).values_list("Check1", flat=True).order_by("-Check1")
    date_v = [data for data in ser_q]
    return np.array(date_v, dtype= np_dtype)

def get_valueList_check2(cellID, start, stop):
    ser_q = LiveStats.objects.filter(CellaID=cellID, Check2__range=(start, stop)).values_list("Check2", flat=True).order_by("-Check2")
    date_v = [data for data in ser_q]
    return np.array(date_v, dtype= np_dtype)

def get_valueList_start(cellID, day):
    ser_q = Stato.objects.filter( CellaID=cellID, Data = day, Stato = True).values_list("Ora", flat=True)
    date_v = [data for data in ser_q]
    for i in range(len(date_v)):
        date_v[i] = datetimeCom(day,str2Time(date_v[i]))
    return np.array(date_v , dtype= np_dtype)

def get_valueList_stop(cellID, day):
    ser_q = Stato.objects.filter( CellaID=cellID, Data = day, Stato = False).values_list("Ora", flat=True)
    date_v = [data for data in ser_q]
    for i in range(len(date_v)):
        date_v[i] = datetimeCom(day,str2Time(date_v[i]))
    return np.array(date_v, dtype= np_dtype)

def get_valueLists_stato(cellID, day):
    ser_q = Stato.objects.filter( CellaID=cellID, Data = day).values("Data", "Ora", "Stato").order_by("-Ora")
    date_v = [data for data in ser_q]
    return date_v

def get_value_lastStato(cellID, day):
    result = Stato.objects.filter( CellaID=cellID, Data = day).values("Ora","Stato","Alarm").last()
    return result

def isCellLive(cellID ,time):
    result = LiveStats.objects.filter( CellaID=cellID,Check1__gt=time)
    return result.exists()

def isDailyStatoChang(cellID, day):
    result = Stato.objects.filter( CellaID=cellID,Data = day)
    return result.exists()

def isStatoIdle(cellID, day, time, alarm_v = 0):
    result = Stato.objects.filter( CellaID=cellID, Data = day, Ora__gt=time, Stato = False, Alarm = alarm_v)
    return result.exists()

def isDailyPezzisChang(cellID, day):
    result = Pezzi.objects.filter( CellaID=cellID, Data = day)
    return result.exists()

def str2Date(datestr):
    return date(*map(int, datestr.split("-")))

def str2Time(timestr):
    return time(*map(int, timestr.split(".")[0].split(":")))

def datetimeCom(date,time):
    return datetime.combine(str2Date(date), time)

def generateTmRange(day):
    start = datetimeCom(day, startTm)
    stop = start + timedelta(hours= 24)
    curr_time = datetime.now()
    stop = stop if stop < curr_time else curr_time
    return start, stop

def convert_to_hhmmss(td_array):
    td = pd.Timestamp('2021-01-01') + pd.Timedelta(td_array)
    td = td.strftime('%H:%M:%S')
    return td

def calcd_dailyLiveTm(cellID, day):
    start, stop = generateTmRange(day)
    check1 = get_valueList_check1(cellID, start, stop)
    check2 = get_valueList_check2(cellID, start, stop)
    deltaTsum = np.timedelta64(0,'us')
    if (check1.size > check2.size):
        check2 = np.append(check2, [np.datetime64(start)])
    if (check1.size == check2.size):
        deltaTsum = (check1-check2).sum()
    if len(check1) == 0:
        check1 = ["null"]
    if len(check2) == 0:
        check2 = ["null"]
    return deltaTsum,check1[0],check2[-1]

def calcd_dailyWorkTm(statolist, stop, start):
    startTms =[]
    stopTms =[]
    for i in range(len(statolist)):
        if statolist[i]["Stato"] == 1:
            startTms.append(datetimeCom(statolist[i]["Data"],str2Time(statolist[i]["Ora"])))
            if i==0 and stop != "null":
                stopTms.append(stop.astype(datetime))
        else:
            stopTms.append(datetimeCom(statolist[i]["Data"],str2Time(statolist[i]["Ora"])))
            if i+1 == len(statolist) and start != "null":
                startTms.append(start.astype(datetime))
    startTms, stopTms = np.array(startTms, dtype= np_dtype), np.array(stopTms, dtype= np_dtype)
    if ( startTms.size == stopTms.size):
        deltaT = (stopTms-startTms)
        return deltaT.sum()
    else:
        return np.timedelta64(0,'us')

def calcd_dailyIdleTm(statolist, stop, start):
    startTms =[]
    stopTms =[]
    for i in range(len(statolist)):
        if statolist[i]["Stato"] == 1:
            startTms.append(datetimeCom(statolist[i]["Data"],str2Time(statolist[i]["Ora"])))
            if i+1 == len(statolist) and start != "null":
                stopTms.append(start.astype(datetime))
        else:
            stopTms.append(datetimeCom(statolist[i]["Data"],str2Time(statolist[i]["Ora"])))
            if i == 0 and stop != "null":
                startTms.append(stop.astype(datetime))
    startTms, stopTms = np.array(startTms, dtype= np_dtype), np.array(stopTms, dtype= np_dtype)
    if ( startTms.size == stopTms.size):
        deltaT = (startTms-stopTms)
        return deltaT.sum()
    else:
        return np.timedelta64(0,'us')

def getDataForIndex(day):
    q_set = LiveStats.objects.values_list("CellaID", flat=True).distinct()
    celleList = [livestats for livestats in q_set]
    output = []
    sub_output = []
    for i in range(len(celleList)):
        if len(sub_output) == 3:
            output.append(sub_output)
            sub_output = []
        subinfo = getCellaDataForIndex(celleList[i], day)
        sub_output.append(subinfo)
    if len(sub_output) > 0:
        output.append(sub_output)
    return output

def getCellaDataForIndex(cellID, day):
    nodeinfo = LiveStats.objects.filter(CellaID = cellID).values_list("Note_Id", flat=True).last()
    output = {"CellaID": cellID, "Note_Id": nodeinfo}
    output["Proc"] = getDailyProcData(cellID, day)
    output["Pezz"] = getDailyPezzData(cellID, day)
    output["Stato"] = getCurrStatoData(cellID)
    return output

def getDailyProcData(cellID, day):
    output={"WorkTm":0, "IldeTm":0, "AbnormTm": 0}
    liveTm, stop, start = calcd_dailyLiveTm(cellID, day)
    output["OnlineTm"] = convert_to_hhmmss(liveTm)
    if isDailyStatoChang(cellID, day):
        statolist = get_valueLists_stato(cellID, day)
        output["WorkTm"] = convert_to_hhmmss(calcd_dailyWorkTm(statolist, stop, start))
        output["IldeTm"] = convert_to_hhmmss(calcd_dailyIdleTm(statolist, stop, start))
    return output

def getCurrStatoData(cellID):
    output = {"AlarmSrt":"无", "Status":"运行中", "img":"aasd.gif", "Mode":"", "Color":"sra2"}
    curr_time = datetime.now() + timedelta(minutes=-5)
    day = curr_time.strftime("%Y-%m-%d")
    if (not isCellLive(cellID, curr_time)):
        return {"AlarmSrt":"无", "Status":"离线中", "img":"aaac.png",  "Mode":"", "Color":"sra4"}
    if (not isDailyStatoChang(cellID, day)):
        output["Status"] = "待机中"
        output["StatoID"] = "ilde" 
        output["Color"] = "sra1"       
    else:
        lastStato = get_value_lastStato(cellID, day)
        if lastStato["Alarm"] > 0:
            output = {"AlarmSrt":get_value_AlarmStr[lastStato["Alarm"]], "Status":"故障中", "img":"aaac.png", "Mode":"seza", "Color":"sra3"}
        elif lastStato["Stato"] ==0:
            output["Status"] = "待机中"
            output["img"] = "aaac.png"
            output["Color"] = "sra1"  
    return output

def getDailyPezzData(cellID, day):
    output = {"Pezzi":"0","ReqPezzi":"0", "TotPezzi":"0", "Reach":"56"}
    if not(isDailyPezzisChang(cellID, day)):
        return output
    pezz_v = get_value_dailyPezzi(cellID, day)
    output["Pezzi"] = pezz_v[1]
    output["ReqPezzi"] = pezz_v[2]
    output["TotPezzi"] = pezz_v[3]  
    output["Reach"] = round((output["Pezzi"]*100/output["TotPezzi"]) )if output["TotPezzi"] >0 else 100
    return output

