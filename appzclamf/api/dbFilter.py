from django.db.models import Q, F, Value, DateTimeField
from django.db.models.functions import Concat, Cast
from django.db.models.expressions import RawSQL
import numpy as np
from numpy.lib.stride_tricks import as_strided
from appzclamf.models import  Alarmi, Pezzi, Stato, LiveState, Order, OrderHistory
from datetime import datetime, timedelta, date, time
import pandas as pd

import pytz
from django.utils.timezone import make_aware

imglink = {
    "CNC全自动双站式花式机":"1.png",
    "全自动机器人钉胶机" : "2.png",
    "多功能高精密五轴机":"3.png",
    "高光机":"4.png",
    "精雕切比一体机":"5.png",
    "全自动开料机":"6.png", 
    "全自动刨比开料机": "7.png",
    "全智能打比机":"8.png",
    "比后工序自动机":"9.png"}

tz = pytz.timezone('Asia/Shanghai')

np_dtype = "datetime64[us]"
startTm = datetime.min.time()



def get_serq_Live(cellID):
    ser_q = LiveState.objects.order_by("-id").filter( CellaID=cellID)
    return ser_q

def get_serq_pezzi(cellID):
    ser_q = Pezzi.objects.filter( CellaID=cellID).order_by("-Id")
    return ser_q

def get_serq_stato(cellID):
    ser_q = Stato.objects.filter( CellaID=cellID).order_by("-Id")
    return ser_q

def get_value_AlarmStr(alarmID):
    ser_q = Alarmi.objects.filter(AllarmID = alarmID)
    return ser_q[0].AllarmString

def get_value_LastPezzi(cellID, orderID):
    date_v = Pezzi.objects.filter( CellaID=cellID, OrderID=orderID).values_list("Pezzi","ReqPezzi","ResidPezzi", "EstimatedTm","TotWorkTm").last()
    return date_v

def get_value_DailyPezzi(cellID, start, stop):
    ser_q = Pezzi.objects.annotate(Dt=Cast('DataTime', output_field= DateTimeField()))
    ser_q = ser_q.filter( CellaID=cellID, Dt__range=(nupDt2DateTime(start), nupDt2DateTime(stop))).values_list("Pezzi", "DataTime")
    return ser_q.count()

def get_value_LastPezzi(cellID, start, stop):
    ser_q = Pezzi.objects.annotate(Dt=Cast('DataTime', output_field= DateTimeField()))
    date_v = ser_q.filter( CellaID=cellID, Dt__range=(nupDt2DateTime(start), nupDt2DateTime(stop))).values_list("Pezzi","ReqPezzi","ResidPezzi", "EstimatedTm","TotWorkTm", "OrderID").last()
    return date_v

def get_valueList_check1(cellID, start, stop):
    ser_q = LiveState.objects.filter(CellaID=cellID, Check1__range=(start, stop)).values_list("Check1", flat=True).order_by("-Check1")
    date_v = [data for data in ser_q]
    return np.array(date_v, dtype= np_dtype)

def get_valueList_check2(cellID, start, stop):
    ser_q = LiveState.objects.filter(CellaID=cellID, Check2__range=(start, stop)).values_list("Check2", flat=True).order_by("-Check2")
    date_v = [data for data in ser_q]
    return np.array(date_v, dtype= np_dtype)

def get_valueList_statoTmF(cellID, start, stop):
    ser_q = Stato.objects.annotate(Dt=Cast('DataTime', output_field= DateTimeField()))
    ser_q = ser_q.filter( CellaID=cellID, Dt__range=(nupDt2DateTime(start), nupDt2DateTime(stop))).values("CellaID","DataTime", "Stato", "Alarm","OrderID").order_by("-DataTime")
    date_v = [data for data in ser_q]
    return date_v

def get_value_Order(orderId):
    date_v = Order.objects.filter( OrderID=orderId).values_list("OrderID","StytleNum","FinishParts","RequireParts", "WorkStatus").last()
    return date_v

def get_value_LastOrderRecord(orderId, cellID):
    date_v = OrderHistory.objects.filter( OrderID=orderId, CellaID = cellID).last()
    return date_v

def get_value_lastStato(cellID, start, stop):
    ser_q = Stato.objects.annotate(Dt=Cast('DataTime', output_field= DateTimeField()))
    result = ser_q.filter( CellaID=cellID, Dt__range=(nupDt2DateTime(start), nupDt2DateTime(stop))).values("Ora","Stato","Alarm", "OrderID").last()
    return result

def isCellOnline(cellID ,time):
    result = LiveState.objects.filter( CellaID=cellID,Check1__gt=time)
    return result.exists()

def isDailyStatoChang(cellID, start, stop):
    ser_q = Stato.objects.annotate(Dt=Cast('DataTime', output_field= DateTimeField()))
    result = ser_q.filter( CellaID=cellID, OrderID__isnull=False, Dt__range=(nupDt2DateTime(start), nupDt2DateTime(stop)))
    return result.exists()

def isStatoIdle(cellID, day, time, alarm_v = 0):
    result = Stato.objects.filter( CellaID=cellID, Data = day, Ora__gt=time, Stato = False, Alarm = alarm_v)
    return result.exists()

def isDailyPezzisChang(cellID, start, stop):
    ser_q = Pezzi.objects.annotate(Dt=Cast('DataTime', output_field= DateTimeField()))
    result = ser_q.filter( CellaID=cellID, Dt__range=(nupDt2DateTime(start), nupDt2DateTime(stop)))
    return result.exists()

def str2Date(datestr):
    return date(*map(int, datestr.split("-")))

def str2Time(timestr):
    return time(*map(int, timestr.split(".")[0].split(":")))

def datetimeCom(date,time):
    return datetime.combine(str2Date(date), time)

def generateTmRange(day):
    start = day
    stop = start + timedelta(hours= 24)
    curr_time = datetime.now(tz)
    curr_time = curr_time.replace(tzinfo=None)
    stop = stop if stop < curr_time else curr_time
    return start, stop

def convert_to_hhmmss(td_array):
    td = pd.Timestamp('2021-01-01') + pd.Timedelta(td_array)
    td = td.strftime('%H:%M:%S')
    return td

def is_zero_one_seq(arr):
    return np.all(np.abs(np.diff(arr)) == 1) and (arr[0] in [0, 1]) and (arr[-1] in [0, 1])

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
        check1 = [datetime.now()]
    if len(check2) == 0:
        check2 = [datetime.combine(datetime.now().date(), datetime.min.time())]
    deltaTsum = convert_to_hhmmss(deltaTsum)
    return deltaTsum,check1[0],check2[-1]

def calcd_dailyWorkTm(statolist, stop, start):
    DtList = np.array([data['DataTime'] for data in statolist], dtype= np_dtype)
    StatoList = np.array([data['Stato'] for data in statolist], dtype= int)
    if StatoList[0] == 1:
        DtList = np.insert(DtList, 0, np.datetime64(stop))
        StatoList = np.insert(StatoList, 0, 0)
    if StatoList[-1] == 0:
        DtList = np.append(DtList, np.datetime64(start))
        StatoList = np.append(StatoList, 1)
    if not is_zero_one_seq(StatoList):
        return convert_to_hhmmss(np.timedelta64(0,'us'))
    DtList = DtList.reshape([2,-1],order="F")
    deltaT = (DtList[0]-DtList[1]).sum()
    deltaT = convert_to_hhmmss(deltaT)
    return deltaT

def calcd_dailyIdleTm(statolist, stop, start):
    DtList = np.array([data['DataTime'] for data in statolist], dtype= np_dtype)
    StatoList = np.array([data['Stato'] for data in statolist], dtype= int)
    if StatoList[0] == 0 and stop != "null" and start != "null":
        DtList = np.insert(DtList, 0, np.datetime64(stop))
        StatoList = np.insert(StatoList, 0, 1)
    if StatoList[-1] == 1 and stop != "null" and start != "null":
        DtList = np.append(DtList, np.datetime64(start))
        StatoList = np.append(StatoList, 0)
    if not is_zero_one_seq(StatoList):
        return convert_to_hhmmss(np.timedelta64(0,'us'))
    DtList = DtList.reshape([2,-1],order="F")
    deltaT = (DtList[0]-DtList[1]).sum()
    deltaT = convert_to_hhmmss(deltaT)
    return deltaT

def getDataForIndex(day):
    q_set = LiveState.objects.values_list("CellaID", flat=True).distinct()
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

def nupDt2DateTime(nupDt):
    if isinstance(nupDt, datetime):
        return nupDt
    return nupDt.astype(datetime)
def getCellaDataForIndex(cellID, day):
    if day == '':
        day = datetime.now(tz).strptime('%Y-%m-%d')
    day = datetime.strptime(day, '%Y-%m-%d')
    nodeinfo = LiveState.objects.filter(CellaID = cellID).values_list("Note_Id", flat=True).last()
    output = {"CellaID": cellID, "Note_Id": nodeinfo, "Note_Img": imglink[nodeinfo]}

    liveTm, stop, start = calcd_dailyLiveTm(cellID, day)
    output["Proc"] = getDailyProcData(cellID, liveTm, stop, start)
    output["Pezz"] = getDailyPezzData(cellID, stop, start)
    output["Stato"] = getCurrStatoData(cellID, stop, start)
    return output

def getDailyProcData(cellID, liveTm, stop, start):
    output={"WorkTm":0, "IldeTm":0, "AbnormTm": 0}
    output["OnlineTm"] = liveTm
    if isDailyStatoChang(cellID, start, stop): 
        statolist = get_valueList_statoTmF(cellID, start, stop)
        output["WorkTm"] = calcd_dailyWorkTm(statolist, stop, start)
        output["IldeTm"] = calcd_dailyIdleTm(statolist, stop, start)
    return output

def getCurrStatoData(cellID, stop, start):
    output = {"AlarmSrt":"无", "Status":"运行中", "img":"aasd.gif", "Mode":"", "Color":"sra2"}
    curr_time = (datetime.now(tz) + timedelta(minutes=-2)).replace(tzinfo=None)

    if (not isCellOnline(cellID, curr_time)):
        return {"AlarmSrt":"无", "Status":"离线中", "img":"aaac.png",  "Mode":"", "Color":"sra4"}
    if (not isDailyStatoChang(cellID, start, stop)): 
        output["Status"] = "待机中"
        output["StatoID"] = "ilde" 
        output["img"] = "aaac.png"
        output["Color"] = "sra1"
    else:
        lastStato = get_value_lastStato(cellID, start, stop)
        if lastStato["Alarm"] > 0:
            output = {"AlarmSrt":get_value_AlarmStr[lastStato["Alarm"]], "Status":"故障中", "img":"aaac.png", "Mode":"seza", "Color":"sra3"}
        elif lastStato["Stato"] ==0 | lastStato["OrderID"].isNull():
            output["Status"] = "待机中"
            output["img"] = "aaac.png"
            output["Color"] = "sra1"  
    return output

def getDailyPezzData(cellID, stop, start):
    output = {"DailyPezzi":"0","Pezzi":"0","ReqPezzi":"0", "TotPezzi":"0", "Reach":"0" ,"OrderID": "", "WorkTm": "", "EstimatedTm": ""}
    if not(isDailyPezzisChang(cellID, start, stop)):
        return output
    pezz_v = get_value_LastPezzi(cellID, start, stop)
    output["DailyPezzi"] = get_value_DailyPezzi(cellID, start, stop)
    output["Pezzi"] = pezz_v[0]
    output["ReqPezzi"] = pezz_v[1]
    output["TotPezzi"] = pezz_v[2]
    output["OrderID"] = pezz_v[5]
    output["WorkTm"] = pezz_v[4]
    output["EstimatedTm"] = pezz_v[3]
    if (output["ReqPezzi"]>0 ):
        output["Reach"] = round((output["Pezzi"]*100/output["ReqPezzi"]))
    output["Reach"] = "--"
    return output

