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
    buildAboutEduList()
    try {
      fetch(`/api/amfui/record/daily?offset=${offset}&itemsPerPage=0`).then(response => response.json()).then(data => {
        generateDashboard(data.data, 'dashboard-content');
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
}

function shiftRight() {
    curr_offset = curr_offset >= maxLen - 1 ? curr_offset : curr_offset + 1;
    fetchDashboardData(curr_offset)
}

function shiftLeft() {
    curr_offset = (curr_offset - 1) < 0 ? curr_offset : curr_offset - 1;
    fetchDashboardData(curr_offset)
}

function buildAboutEduList() {
    const container = document.querySelector('.about_edu');
    const edulistDiv = document.createElement('div');
    edulistDiv.className = 'about_edulist';

    const ul = document.createElement('ul');
    ul.className = 'clearfix';
  
    const li = document.createElement('li');
    li.className = 'clearfix';
  
    const flexDiv = document.createElement('div');
    flexDiv.className = 'flex-column align-center';
  
    const innerDiv = document.createElement('div');
    innerDiv.style.width = '18rem';
  
    const dashboardContent = document.createElement('div');
    dashboardContent.id = 'dashboard-content';
    dashboardContent.className = 'pt-6 flex-row flex-wrap justify-between';
  
    innerDiv.appendChild(dashboardContent);
    flexDiv.appendChild(innerDiv);
    li.appendChild(flexDiv);
    ul.appendChild(li);
    edulistDiv.appendChild(ul);
    container.appendChild(edulistDiv);
  }

function generateDashboard(objList, element) {
    const boxContent = document.getElementById(element);
    maxLen = objList.length;
    objList.slice(0, 1).forEach(obj => {
        const cellQ = perpareCellInfo(obj);
        const box = document.createElement('div');
        box.className = 'box-b pd-3 flex-column postion-relative';
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

function addBtnActionForTuch() {
    const touchArea = document.getElementById('touchArea');
    let startX, endX;
   
    touchArea.addEventListener('touchstart', function(e) {
      startX = e.touches[0].clientX;
    });   
    touchArea.addEventListener('touchmove', function(e) {
      e.preventDefault(); // 防止页面滚动
    });   
    touchArea.addEventListener('touchend', function(e) {
      endX = e.changedTouches[0].clientX;
      if (endX - startX > 0) {
        shiftRight();
      } else {
        shiftLeft();
      }
    });
}

function perpareCellInfo(cellQ) {
    rate=0
    if(cellQ.worksheet_finish > 0)
    {
        rate = cellQ.worksheet_finish*100/cellQ.worksheet_req
    }
    estimated = cellQ.worksheet_estimated;
    if(cellQ.worksheet_estimated == 0 && rate < 100)
        estimated = "?"
    var result = {
        "name": cellQ.cell_name,
        "id": cellQ.cell_id,
        "index": cellQ.cell_id + "-" + cellQ.cell_name,
        "plant": cellQ.cell_plant,
        "alarm": cellQ.cell_alarm,
        "status": cellQ.cell_status,
        "daily_online": cellQ.daily_online,
        "daily_adjust": cellQ.daily_adjust,
        "daily_poweron": cellQ.daily_poweron,
        "daily_idle": cellQ.daily_idle,
        "daily_work": cellQ.daily_job,
        "daily_finish": cellQ.daily_finish,
        "order_id": cellQ.worksheet_orderId,
        "process": cellQ.worksheet_process,
        "product_id": cellQ.worksheet_productId, 
        "ws_id": cellQ.worksheet_id,
        "ws_req": cellQ.worksheet_req,        
        "ws_remain": cellQ.worksheet_req - cellQ.worksheet_finish,
        "ws_finish": cellQ.worksheet_finish,
        "ws_status": cellQ.worksheet_status,
        "ws_estimate": estimated,
        "ws_finish_rate": rate,
        "ws_pcsTime": cellQ.worksheet_pieceTm,
        "DailyTm": cellQ.daily_tm
    };
    if (cellQ.cell_alarm == null || cellQ.cell_alarm =='')
    {   result.alarm = '无异常';     }
    if (cellQ.cell_status == '作业中')
    {   result.status_clore = "sra2"; }
    else if (cellQ.cell_status == '待机')
    {   result.status_clore = "sra1"; }
    else if (cellQ.cell_status == '离线')
    {   result.status_clore = "sra4"; }
    else{   result.status_clore = "sra3";   }
    return result;
}

function createBoxTitle(cellQ) {
    const boxTitle = document.createElement('div');
    boxTitle.id = 'box_tatle';
    boxTitle.className = 'pt-7 pl-7 font-s10 color-blue postion-relative';
    
    const titleText = document.createTextNode(cellQ.index);
    boxTitle.appendChild(titleText);
    
    const hengx = document.createElement('div');
    hengx.className = 'hengx postion-absolute';
    boxTitle.appendChild(hengx);			
    return boxTitle;
}
function createBoxBody(cellQ) {
    const boxBody = document.createElement('div');
    boxBody.style.width = '17rem';
    boxBody.className = 'pt-13 flex-row justify-between';

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
    orderReport.style.width = '8.0rem';

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
    infoContainer.className = 'dingdanshu flex-row justify-between flex-3 pt-5';
    if(type == 'plan')
    {
        infoContainer.appendChild(createInfoElement('订单号', cellQ.order_id));
        infoContainer.appendChild(createInfoElement('工序', cellQ.process));
    }else{
        infoContainer.appendChild(createInfoElement('总数量', cellQ.ws_req));
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
    valueDiv.className = 'fep-12c font-weight-bold';
    valueDiv.textContent = value;
    element.appendChild(valueDiv);

    return element;
}
function createStatoReport(cellQ) {
    const statoReport = document.createElement('div');
    statoReport.className = 'zhuangt';
    statoReport.style.width = '8rem';

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
    recordDetails.className = 'pt-6';

    const PcsTime = document.createElement('div');
    PcsTime.className = 'sez font-weight-normal';
    PcsTime.textContent = '单件加工 : ' + cellQ.ws_pcsTime;
    recordDetails.appendChild(PcsTime)

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

    const estimatedinfo = document.createElement('div');
    estimatedinfo.className = 'fep-12b font-weight-normal';
    estimatedinfo.textContent = '( ' + cellQ.DailyTm + ' H/Day )';
    progress.appendChild(estimatedinfo);
    return progress;
}



