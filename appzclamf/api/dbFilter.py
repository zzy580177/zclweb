import math
from django.db.models import Q, F, Value, DateTimeField, DateField
from django.db.models.functions import Concat, Cast, TruncDate
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

def str_time_to_s(str_time):
    if str_time.__contains__(":") == False:
        return 0
    time_parts = str_time.split(':')
    time_parts = [math.fabs(float(num)) for num in time_parts]
    hours, minutes, seconds = map(int, time_parts)
    dt_object = time(hour=hours, minute=minutes, second=seconds)
    since_midnight = dt_object.hour * 3600 * 10**9  + dt_object.minute * 60 * 10**9 + dt_object.second * 10**9
    return since_midnight

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

def get_value_workSheetPezzi(cellID, workSheetID):
    date_v = Pezzi.objects.filter( CellaID=cellID, WorkSheetID=workSheetID).values_list("Pezzi","ReqPezzi","ResidPezzi", "EstimatedTm","TotWorkTm").last()
    return date_v

def get_value_DailyPezzi(cellID, day):    
    ser_q = Pezzi.objects.annotate(date=Cast('DataTime', output_field= DateField()))
    ser_q = ser_q.filter( CellaID=cellID, date = day).values_list("Pezzi", "DataTime")
    return ser_q.count()

def get_value_LastPezzi(cellID):
    date_v = Pezzi.objects.filter( CellaID=cellID).last()
    return date_v

def get_dailyRecord(cellID, day):
    ser_q = OrderHistory.objects.annotate(startday=Cast('StartTime', output_field= DateField()), startTM=Cast('StartTime', output_field= DateTimeField()))
    ser_q = ser_q.filter(CellaID= cellID, startday= day).order_by("StartTime")

    PowerOnTMs =  np.array([str_time_to_s(data.PowerOnTM) for data in ser_q])
    WorkingTMs =  np.array([str_time_to_s(data.WorkingTM) for data in ser_q])

    adjSer_q = ser_q.filter(Mode = "调校模式")
    adjPowerOnTMs =  np.array([str_time_to_s(data.PowerOnTM) for data in adjSer_q])
    adjWorkingTMs =  np.array([str_time_to_s(data.WorkingTM) for data in adjSer_q])
    result ={"PowonTM":"", "WorkTM":"", "AdjTM":"", "IdlTM":""};

    result["PowonTM"] = convert_to_hhmm(PowerOnTMs.sum())
    result["WorkTM"] = convert_to_hhmm(WorkingTMs.sum() - adjWorkingTMs.sum())
    result["AdjTM"] = convert_to_hhmm(adjPowerOnTMs.sum())
    result["IdlTM"] = convert_to_hhmm(PowerOnTMs.sum()-adjPowerOnTMs.sum()- WorkingTMs.sum() - adjWorkingTMs.sum())
    result["StartTM"] = ser_q.first().startTM if ser_q.first() != None else ""
    result["PowonMs"] = int(PowerOnTMs.sum())/10**3
    return result

def change_EstimatedTm(date):
    if date.__contains__(".") == True:
        tmp = date.split(".")
        day = ""; tm= tmp[0]
        if tm.__contains__(":") != True:
            day = tmp[0]+"D ";tm= tmp[1]
        return day +tm.split(":")[0]+"H " + tm.split(":")[1] + "M "
    else:
        return date

def get_valueList_check1(cellID, day):    
    ser_q = LiveState.objects.annotate(Dt=Cast('Check1', output_field= DateField()))
    ser_q = ser_q.filter(CellaID=cellID, Dt = day).values_list("Check1", flat=True).order_by("-Check1")
    date_v = [data for data in ser_q]
    return np.array(date_v, dtype= np_dtype)

def get_valueList_check2(cellID, day):
    ser_q = LiveState.objects.annotate(Dt=Cast('Check2', output_field= DateField()))
    ser_q = ser_q.filter(CellaID=cellID, Dt = day).values_list("Check2", flat=True).order_by("-Check2")
    date_v = [data for data in ser_q]
    return np.array(date_v, dtype= np_dtype)

def get_valueList_statoTmF(cellID, day):
    ser_q = Stato.objects.annotate(Dt=Cast('DataTime', output_field= DateField()))
    ser_q = ser_q.filter( CellaID=cellID, Dt=day).values("CellaID","DataTime", "Stato", "Alarm","WorkSheetID").order_by("-DataTime")
    date_v = [data for data in ser_q]
    return date_v

def get_value_lastStato(cellID, day):
    ser_q = Stato.objects.annotate(Dt=Cast('DataTime', output_field= DateField()))
    result = ser_q.filter( CellaID=cellID, Dt=day).values("DataTime","Stato","Alarm", "WorkSheetID").last()
    return result

def getOrderList():
    ser_q = Order.objects.all()
    date_v = [data for data in ser_q]
    return date_v

def getUnFinishOrderList(cellID):
    ser_q = Order.objects.filter(CellaID=cellID,WorkStatus = "就绪")
    date_v = [data for data in ser_q]
    return date_v

def getOrderInfoFromWorkSheet(cellID):
    date_v = Order.objects.filter(CellaID=cellID, WorkStatus = "加工中").last()
    return date_v

def getOrderListDetail():
    #ser_q = Order.objects.annotate(Dt=Cast('DataTime', output_field= DateTimeField()))
    ser_q = Order.objects.all().order_by("WorkStatus")
    date_v = [data for data in ser_q]
    result =[]
    for data in date_v:
        dataDic = {"CellaID": data.CellaID,"Colour":data.Colour,"AddReqParts":data.AddReqParts, "FinishParts":data.FinishParts, "OrderID": data.OrderID, "Process": data.Process, "RequireParts": data.RequireParts, "StytleNum": data.StytleNum, "WorkStatus": data.WorkStatus}
        tmp = {"WorkSheetID": data.WorkSheetID, "startTM": "", "endTM": "", "WorkTM": "--", "IdlTM": "--","AdjTM":"--", "EstimatedTime": "--"}
        if data.WorkStatus == "已完成" or data.WorkStatus== "暂停" :
            tmp.update(getWorkSheetRecordFromHistory(data.WorkSheetID, data.CellaID))
        elif data.WorkStatus == "加工中":
            tmp.update(getWorkSheetRecordFromOngoing(data.WorkSheetID, data.CellaID))
        dataDic.update(tmp)
        nodeinfo = LiveState.objects.filter(CellaID = data.CellaID).values_list("Note_Id", flat=True).last()
        result.append(dataDic)
    return result

def getWorkSheetRecordFromHistory(worksheetID, cellaID):
    ser_q = OrderHistory.objects.filter(WorkSheetID = worksheetID, CellaID= cellaID).order_by("StartTime")
    PowerOnTMs =  np.array([str_time_to_s(data.PowerOnTM) for data in ser_q])
    WorkingTMs =  np.array([str_time_to_s(data.WorkingTM) for data in ser_q])

    adjSer_q = ser_q.filter(Mode = "调校模式")
    adjPowerOnTMs =  np.array([str_time_to_s(data.PowerOnTM) for data in adjSer_q])
    adjWorkingTMs =  np.array([str_time_to_s(data.WorkingTM) for data in adjSer_q])

    WorkTmSum = convert_to_hhmmss(WorkingTMs.sum() - adjWorkingTMs.sum())
    AdjTmSum = convert_to_hhmmss(adjPowerOnTMs.sum())
    IdlTmsum = convert_to_hhmmss(PowerOnTMs.sum()-adjPowerOnTMs.sum()- WorkingTMs.sum() - adjWorkingTMs.sum())
    result = {"workSheetID": worksheetID, "startTM": time2Date(ser_q.first().StartTime), "endTM": time2Date(ser_q.last().StopTime), "WorkTM": WorkTmSum, "AdjTM": AdjTmSum, "IdlTM":IdlTmsum}
    return result

def getWorkSheetRecordFromOngoing(worksheetID, cellaID):
    ser_q = OrderHistory.objects.filter(WorkSheetID = worksheetID, CellaID = cellaID).order_by("StartTime")
    PowerOnTMs =  np.array([str_time_to_s(data.PowerOnTM) for data in ser_q])
    WorkingTMs =  np.array([str_time_to_s(data.WorkingTM) for data in ser_q])

    adjSer_q = ser_q.filter(Mode = "调校模式")
    adjPowerOnTMs =  np.array([str_time_to_s(data.PowerOnTM) for data in adjSer_q])
    adjWorkingTMs =  np.array([str_time_to_s(data.WorkingTM) for data in adjSer_q])

    WorkTmSum = convert_to_hhmmss(WorkingTMs.sum() - adjWorkingTMs.sum())
    AdjTmSum = convert_to_hhmmss(adjPowerOnTMs.sum())
    IdlTmsum = convert_to_hhmmss(PowerOnTMs.sum()-adjPowerOnTMs.sum()- WorkingTMs.sum() - adjWorkingTMs.sum())
    pezzis= get_value_workSheetPezzi(cellaID, worksheetID) 
    result = {"workSheetID": worksheetID, "startTM": time2Date(ser_q.first().StartTime) if ser_q.first() else "", "endTM": "--", "WorkTM": WorkTmSum, "AdjTM": AdjTmSum, "IdlTM":IdlTmsum}
    if(pezzis):
        result["FinishParts"] = pezzis[0]
        result['EstimatedTime'] = change_EstimatedTm(pezzis[3])
    return result

def time2Date(time):
    return time.split()[0].replace("-","/")

def addNewOrder(order):
    orderNum = Order.objects.all().count()%255
    worksheetID = "GD"+ datetime.now().strftime("%y%m%d_") + str(orderNum)
    instance = Order.objects.create(WorkStatus="未就绪", WorkSheetID=worksheetID, StytleNum=order["StytleNum"], OrderID=order["OrderID"], Process=order["Process"], Colour=order["Colour"], RequireParts=order["RequireParts"])
    return instance

def updateOrderList(ser_q):
    for i in range(0, len(ser_q)):
        if ser_q[i]['StytleNum'] != "None" or ser_q[i]['Colour'] != "None" or ser_q[i]['Process'] != "None":
            Order.objects.filter(WorkSheetID=ser_q[i]['WorkSheetID']).update(StytleNum=ser_q[i]['StytleNum'], Colour=ser_q[i]['Colour'], Process=ser_q[i]['Process'])

def DelFromOrderList(delList):
    for worksheetID in delList:
        Order.objects.filter(WorkSheetID=worksheetID).delete()

def getWorkRecordList(cellID):
    ser_q = OrderHistory.objects.filter( CellaID=cellID).order_by("-StartTime")
    date_v = [data for data in ser_q]
    return date_v

def isCellOnline(cellID ,time):
    result = LiveState.objects.filter( CellaID=cellID,Check1__gt=time)
    return result.exists()

def isDailyStatoChang(cellID, day):
    ser_q = Stato.objects.annotate(Dt=Cast('DataTime', output_field= DateField()))
    result = ser_q.filter( CellaID=cellID, WorkSheetID__isnull=False, Dt=day)
    return result.exists()

def isStatoIdle(cellID, day, time, alarm_v = 0):
    result = Stato.objects.filter( CellaID=cellID, Data = day, Ora__gt=time, Stato = False, Alarm = alarm_v)
    return result.exists()

def isDailyPezzisChang(cellID, day):
    ser_q = Pezzi.objects.annotate(date=Cast('DataTime', output_field= DateField()))
    result = ser_q.filter( CellaID=cellID, date=day)
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

def convert_to_hhmm(td_array):
    td = pd.Timestamp('2021-01-01') + pd.Timedelta(td_array)
    td = td.strftime('%H:%M')
    return td

def is_zero_one_seq(arr):
    return np.all(np.abs(np.diff(arr)) == 1) and (arr[0] in [0, 1]) and (arr[-1] in [0, 1])

def calcd_dailyLiveTm(cellID, day, start):
    check1 = get_valueList_check1(cellID, day)
    check2 = get_valueList_check2(cellID, day)
    deltamMs = np.timedelta64(0,'us')
    if (check1.size > check2.size):
        check2 = np.append(check2, [np.datetime64(start)])
    if (check1.size == check2.size):
        deltamMs = (check1-check2).sum()
    if len(check1) == 0:
        check1 = [datetime.now(tz)]
    if len(check2) == 0:
        check2 = [datetime.combine(datetime.now(tz).date(), datetime.min.time())]
    deltaTsum = convert_to_hhmm(deltamMs)
    if (isDailyStatoChang(cellID, day)):
        statoList = get_valueList_statoTmF(cellID,day)
        return deltaTsum,deltamMs.astype('int64'),calcd_dailyWorkTm(statoList,check1[0],check2[-1]),calcd_dailyIdleTm(statoList,check1[0],check2[-1])
    else:
        return deltaTsum,deltamMs.astype('int64'),0,0

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
    deltaT = convert_to_hhmm(deltaT)
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
    deltaT = convert_to_hhmm(deltaT)
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
        day = datetime.now(tz).strftime('%Y-%m-%d')
    day = datetime.strptime(day, '%Y-%m-%d')
    nodeinfo = LiveState.objects.filter(CellaID = cellID).values_list("Note_Id", flat=True).last()
    output = {"CellaID": cellID, "Note_Id": nodeinfo, "Note_Img": imglink[nodeinfo]}

    output["Proc"] = get_dailyRecord(cellID, day)
    output["Proc"]["OnlineTM"],onlineTmsum, output["Proc"]["OnlineWorkTM"],output["Proc"]["OnlineIdlTM"] = calcd_dailyLiveTm(cellID, day, output["Proc"]["StartTM"])
    output["Proc"]["OfflineRate"] = round((output["Proc"]["PowonMs"]-onlineTmsum)*100/output["Proc"]["PowonMs"]) if output["Proc"]["PowonMs"] > 0 else "--"
    output["Pezz"] = getDailyPezzData(cellID, day)
    output["Stato"] = getCurrStatoData(cellID, day)
    orderlist = getUnFinishOrderList(cellID)
    output["IdlOrder"] = [data.OrderID for data in orderlist]
    return output

def getCurrStatoData(cellID, day):
    output = {"AlarmSrt":"无", "Status":"运行中", "img":"aasd.gif", "Mode":"", "Color":"sra2", "WorkMode":""}
    curr_time = (datetime.now(tz) + timedelta(minutes=-2)).replace(tzinfo=None)
    
    OrderRecord = OrderHistory.objects.filter(CellaID= cellID).order_by("StartTime").last()

    if (not isCellOnline(cellID, curr_time)):
        return {"AlarmSrt":"无", "Status":"离线中", "img":"aaac.png",  "Mode":"", "Color":"sra4"}
    if (not isDailyStatoChang(cellID, day)): 
        output["Status"] = "待机中"
        output["StatoID"] = "ilde" 
        output["img"] = "aaac.png"
        output["Color"] = "sra1"
    else:
        lastStato = get_value_lastStato(cellID, day)
        if lastStato["Alarm"] > 0:
            alarmStr = get_value_AlarmStr(lastStato["Alarm"])
            output = {"AlarmSrt":alarmStr, "Status":"故障中", "img":"aaac.png", "Mode":"seza", "Color":"sra3"}
        elif lastStato["Stato"] ==0 or lastStato["WorkSheetID"]== "":
            output["Status"] = "待机中"
            output["img"] = "aaac.png"
            output["Color"] = "sra1"  
    output["WorkMode"] = OrderRecord.Mode
    if output["WorkMode"]=="调校模式":
        output["Status"] = "调机/"+ output["Status"]
    return output

def getDailyPezzData(cellID, day):
    output = {"DailyPezzi":"0","Pezzi":"0","ReqPezzi":"0", "TotPezzi":"0", "Reach":"0" ,"WorkSheetID": "", "WorkTm": "", "EstimatedTm": ""}
    pezz_v = get_value_LastPezzi(cellID)
    orderInfo = getOrderInfoFromWorkSheet(cellID)
    if pezz_v:
        pezz_v = None if pezz_v.WorkSheetID != orderInfo.WorkSheetID else pezz_v
    output["DailyPezzi"] = get_value_DailyPezzi(cellID, day)
    output["Pezzi"] = pezz_v.Pezzi if pezz_v else ""
    output["ReqPezzi"] = pezz_v.ReqPezzi if pezz_v else ""
    output["TotPezzi"] = pezz_v.ResidPezzi if pezz_v else ""
    output["WorkSheetID"] = orderInfo.WorkSheetID if orderInfo else ""  
    output["OrderID"] = orderInfo.OrderID if orderInfo else ""
    output["WorkTm"] = pezz_v.TotWorkTm if pezz_v else ""
    output["EstimatedTm"] = change_EstimatedTm(pezz_v.EstimatedTm) if pezz_v else ""
    output["Reach"] = "--"
    if (output["ReqPezzi"]>0 ):
        output["Reach"] = round((output["Pezzi"]*100/output["ReqPezzi"]))
    return output

