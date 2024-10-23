const imglink = {
    "CNC全自动双站式花式机":"/static/amfui/img/1.png",
    "全自动机器人钉胶机" : "/static/amfui/img/2.png",
    "多功能高精密五轴机":"/static/amfui/img/3.png",
    "高光机":"/static/amfui/img/4.png",
    "精雕切比一体机":"/static/amfui/img/5.png",
    "全自动开料机":"/static/amfui/img/6.png", 
    "全自动刨比开料机": "/static/amfui/img/7.png",
    "智能打比机":"/static/amfui/img/8.png",
    "比后工序自动机":"/static/amfui/img/9.png"
}
curr_offset=0
maxLen = 0
function fetchDashboardData(offset) {
    try {
      fetch(`/api/amfui/live_state_manage/live_state_manage_join?offset=${offset}&itemsPerPage=0`).then(response => response.json()).then(data => {
        generateDashboard(data.data, 'dashboard-content');
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
}

function shiftRight() {
    curr_offset = (curr_offset + 3) > maxLen ? curr_offset : curr_offset + 3;
    fetchDashboardData(curr_offset)
}

function shiftLeft() {
    curr_offset = (curr_offset - 3) < 0 ? curr_offset : curr_offset - 3;
    fetchDashboardData(curr_offset)
}

function generateDashboard(objList, element) {
    const boxContent = document.getElementById(element);
    boxContent.innerHTML = ''; 
    maxLen = objList.length;
    objList.slice(0, 3).forEach(obj => {
        const cellQ = perpareCellInfo(obj);
        const box = document.createElement('div');
        box.className = 'box-a pd-3 flex-column postion-relative';
        box.appendChild(createBoxTitle(cellQ));
        box.appendChild(createBoxBody(cellQ));		
        box.appendChild(createImgsDiv(cellQ));
        boxContent.appendChild(box);
    });
}

function addBtnAction() {
    const leftBtn = document.getElementById('edu_leftbtn');
    const rgBtn = document.getElementById('edu_btn');
    rgBtn.addEventListener('click', function() { shiftRight();});
    leftBtn.addEventListener('click', function() { shiftLeft();});
}

function perpareCellInfo(cellQ) {
    rate=0
    if(cellQ.WorkSheet__FinishParts > 0)
    {
        rate = cellQ.WorkSheet__FinishParts*100/cellQ.TotReq
    }
    var result = {
        "name": cellQ.Cell__Name,
        "id": cellQ.Cell__CellID,
        "index": cellQ.Cell__CellID + "-" + cellQ.Cell__Name,
        "plant": cellQ.Cell__Plant,
        "alarm": cellQ.Alarmi__AlarmString,
        "status": cellQ.CellStatus,
        "daily_online": cellQ.tot_online,
        "daily_adjust": cellQ.tot_adjustTM,
        "daily_poweron": cellQ.tot_poweron,
        "daily_idle": cellQ.tot_idleTM,
        "daily_work": cellQ.tot_workTM,
        "daily_finish": cellQ.tot_parts,
        "ws_id": cellQ.WorkSheet_id,
        "ws_req": cellQ.TotReq,        
        "ws_remain": cellQ.TotReq- cellQ.WorkSheet__FinishParts,
        "ws_finish": cellQ.WorkSheet__FinishParts,
        "ws_status": cellQ.WorkSheet__Status,
        "ws_estimate": cellQ.EstimatedSec,
        "ws_finish_rate": rate,
    };
    if (cellQ.Alarmi__AlarmString == null || cellQ.Alarmi__AlarmString =='')
    {   result.alarm = '无异常';     }
    if (cellQ.CellStatus == '作业中')
    {
        result.status_clore = "sra2";
    }else if (cellQ.CellStatus == '待机')
    {
        result.status_clore = "sra1";
    }else if (cellQ.CellStatus == '离线')
    {
        result.status_clore = "sra4";
    }
    else{
        result.status_clore = "sra3";
    }
    return result;
}

function createBoxTitle(cellQ) {
    const boxTitle = document.createElement('div');
    boxTitle.id = 'box_tatle';
    boxTitle.className = 'pt-2 pl-2 font-s4 color-blue postion-relative';
    
    const titleText = document.createTextNode(cellQ.index);
    boxTitle.appendChild(titleText);
    
    const hengx = document.createElement('div');
    hengx.className = 'hengx postion-absolute';
    boxTitle.appendChild(hengx);			
    return boxTitle;
}
function createBoxBody(cellQ) {
    const boxBody = document.createElement('div');
    boxBody.style.width = '5rem';
    boxBody.className = 'pt-4 flex-row justify-between';

    boxBody.appendChild(createOrderReport(cellQ));
    boxBody.appendChild(createStatoReport(cellQ));
    return boxBody;
}

function createImgsDiv(cellQ) {
    const imgsDiv = document.createElement('div');
    imgsDiv.className = "paruct align-center";
    const img1 = document.createElement('img');
    img1.src =  imglink[cellQ.name];
    img1.className = "tupas";
    imgsDiv.appendChild(img1);
    const img2 = document.createElement('img');
    img2.src =  "/static/amfui/img/aaac.png";
    if (cellQ.status == "作业中")
    {
        img2.src =  "/static/amfui/img/aasd.gif";
    }
    img2.className = "tupasa";
    imgsDiv.appendChild(img2);
    return imgsDiv;
}

function createOrderReport(cellQ) {
    const orderReport = document.createElement('div');
    orderReport.className = 'dingdal';
    orderReport.style.width = '2.0rem';

    const title = document.createElement('div');
    title.className = 'tel font-weight-bold';
    title.textContent = '订单信息';
    orderReport.appendChild(title);			
    orderReport.appendChild(createPezzReport(cellQ,'plan'));	
    const hengg1 = document.createElement('div');
    hengg1.className = 'hengg';
    orderReport.appendChild(hengg1);
    orderReport.appendChild(createPezzReport(cellQ,'real'));
    const hengg2 = document.createElement('div');
    hengg2.className = 'hengg';
    orderReport.appendChild(hengg2);
    orderReport.appendChild(createProgressReport(cellQ));
    
    return orderReport;
}
function createPezzReport(cellQ, type)
{
    const infoContainer = document.createElement('div');
    infoContainer.className = 'dingdanshu flex-row justify-between flex-1 pt-2';
    if(type == 'plan')
    {
        infoContainer.appendChild(createInfoElement('工单号', cellQ.ws_id));
        infoContainer.appendChild(createInfoElement('订单总数量', cellQ.ws_req));
    }else{
        infoContainer.appendChild(createInfoElement('已生产', cellQ.ws_finish));
        infoContainer.appendChild(createInfoElement('待生产', cellQ.ws_remain));	
    }
    return infoContainer;
}
function createInfoElement(label, value) {
    const element = document.createElement('div');
    element.className = 'dingdanshul';

    const labelDiv = document.createElement('div');
    labelDiv.className = 'fep-12';
    labelDiv.textContent = label;
    element.appendChild(labelDiv);

    const valueDiv = document.createElement('div');
    valueDiv.className = 'fep-16 font-weight-bold';
    valueDiv.textContent = value;
    element.appendChild(valueDiv);

    return element;
}
function createStatoReport(cellQ) {
    const statoReport = document.createElement('div');
    statoReport.className = 'zhuangt';
    statoReport.style.width = '2.4rem';

    const status = document.createElement('div');
    status.className = 'yuxnzt font-weight-bold';
    status.textContent = '设备状态: ';
    const statusValue = document.createElement('span');
    statusValue.className = cellQ.status_clore;
    statusValue.textContent = cellQ.status;
    status.appendChild(statusValue);
    statoReport.appendChild(status);

    const dailyRecord = document.createElement('div');
    dailyRecord.className = 'yuxnztjl font-weight-bold';

    const recordTitle = document.createElement('div');
    recordTitle.className = 'fep-16 font-weight-bold';
    recordTitle.textContent = '今日生产记录';
    dailyRecord.appendChild(recordTitle);

    const recordDetails = document.createElement('div');
    recordDetails.className = 'pt-2';

    const onlineTime = document.createElement('div');
    onlineTime.className = 'sez font-weight-normal';
    onlineTime.textContent = '今日在线时长 : ' + cellQ.daily_poweron;
    recordDetails.appendChild(onlineTime);

    const dailyProduction = document.createElement('div');
    dailyProduction.className = 'sez font-weight-normal';
    dailyProduction.textContent = '今日生产数量 : '+ cellQ.daily_finish;
    recordDetails.appendChild(dailyProduction);

    const alarmInfo = document.createElement('div');
    if (cellQ.alarm == '无异常') {
        alarmInfo.className = 'sez font-weight-normal';
    } else {
        alarmInfo.className = 'sez font-weight-normal seza';
    }
    alarmInfo.textContent = '故障信息 : ' + cellQ.alarm;
    recordDetails.appendChild(alarmInfo);

    dailyRecord.appendChild(recordDetails);
    statoReport.appendChild(dailyRecord);

    return statoReport;
}
function createProgressReport(cellQ) {
        
    const progress = document.createElement('div');
    progress.className = 'jintud';

    const progressTitle = document.createElement('div');
    progressTitle.className = 'fep-12b font-weight-normal';
    progressTitle.textContent = '订单加工'+ cellQ.ws_finish_rate.toFixed(1) +"%";
    progress.appendChild(progressTitle);

    const progressBar = document.createElement('progress');
    progressBar.id = 'myProgress' + cellQ.id;
    progressBar.className = 'mypro';
    progressBar.value = Math.round(cellQ.ws_finish_rate);
    progressBar.max = 100;
    progress.appendChild(progressBar);

    const estimatedTime = document.createElement('h3');
    estimatedTime.className = 'fep-12b font-weight-normal';
    estimatedTime.textContent = '预计剩余时长 ' + cellQ.ws_estimate;
    progress.appendChild(estimatedTime);
    return progress;
}



