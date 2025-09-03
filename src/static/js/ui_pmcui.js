import {fetchDataRenderFrame, renderTableAndLoadData, TablerHandler} from './eventAction.js';
import {utils, URLConfig } from './utils.js';
import {API_CONFIG} from './apiConfig.js';
import {partDescriptions, subgongyiGroup, descriptionsTable, updateSelecterSaveButtonState,
    selecterRenderer, tableRenderer, transferRenderer } from './renderFrame.js';



const filter_inputs = ["FNumber","FModel","Status"];

export class ProcRouteEditer extends TablerHandler{
    constructor(container, method){
        super(container.querySelector('.el-descriptions__body table'), method);
        this.container = container;
        this.selecter = container.querySelector('.el-descriptions__extra select')
        this.selectHelp = container.querySelector('#selected_route_note')
        this.target = this.table.querySelector('tbody')
        this.partInfo = JSON.parse(this.table.dataset.orderPart||'{}')
        this.selectHelpText = `订单: ${this.partInfo.POrder_id||''}  零件: ${this.partInfo.FModel||''} 选择加工工艺流程编号: `
    }

    async update(target = this.target) {
        if (!this.table) return console.error('Table not found') || false;
        this.result = this._getData(target);
        return this.result === 'ok' 
            ? await renderTableAndLoadData(this.table, this.method, this.data, 
                this.toggleLoad, descriptionsTable)
            : this.result;
    }

    static selectedRouteSave(container)
    {}
    deleteProcess(){
        this.deleteRow()
        this.table.dataset.endpoint = ''
        this.selectHelp.textContent = this.selectHelpText
        updateSelecterSaveButtonState(this.container, this.table.dataset.endpoint)
    }
    newProcess(data){
        const routeRender = new descriptionsTable(this.table)
        if(!this.table.querySelector('thead')) {
            routeRender.render({items:[data]});
        }
        else if(!this.target){
            routeRender.data = [data];
            routeRender.createBody()
        }else{
            const tr = routeRender.createRow(data);
            this.target.appendChild(tr);
        }
        this.table.dataset.endpoint = ''
        this.selectHelp.textContent = this.selectHelpText
        updateSelecterSaveButtonState(this.container, this.table.dataset.endpoint)
    }
    editProcess(data, rowIdx){
        const routeRender = new descriptionsTable(this.table);
        const rows = this.table.querySelectorAll('tbody tr');
        if(rowIdx !== undefined && rowIdx >= 1 && rowIdx < rows.length) {
            const targetRow = rows[rowIdx-1];
            routeRender.updateRow(targetRow, data);
        }
        this.table.dataset.endpoint = ''
        this.selectHelp.textContent = this.selectHelpText
        updateSelecterSaveButtonState(this.container, this.table.dataset.endpoint)
    }
    async selectOptionLoad()
    {
        const selecterRender = new selecterRenderer(this.selecter)
        await fetchDataRenderFrame(selecterRender)
    }
    async selectedRouteLoad()
    {
        const routeId = this.selecter.value;
        if (!routeId) return;
        this.table.dataset.endpoint = routeId;
        this.selectHelp.textContent = `${this.selectHelpText}${routeId} `
        updateSelecterSaveButtonState(this.container, this.table.dataset.endpoint)
        const tableRender = new descriptionsTable(this.table);
        await fetchDataRenderFrame(tableRender); 
        selecterRenderer.change(this.selecter);
        
        const isSubPart = this.container.dataset['isSubPart']=='true'
        if(isSubPart) return
        renderSubgongyiFrame(document.querySelector('#parts-descriptions-subgongyi'), this.selecter);
    }
    static processEditTriger(table, row)
    {
        const tbody = table.querySelector('tbody');
        const modal = document.getElementById('process-design-modal');
        utils.switchOverlay(modal, true);        
        modal.dataset.url = table.dataset.orderPart;
        modal.dataset.orderPart = table.dataset.orderPart;
        modal.dataset.SeqNum = row? row.rowIndex : tbody?.rows?.length + 1 || 1;
        modal.dataset.mode = row? 'edit' : 'create';
        new ProcessEditer(modal).initModel();  
    }
    static async routeEditTriger(modal, button) {    
        if (button.classList.contains('btn-active')) {
            button.classList.remove('btn-active');
            partDescriptions.toggleEditButtons(modal, false);
        }
        else{
            button.classList.toggle('btn-active', true);
            const partDesc = new partDescriptions(
                modal.querySelector('#parts-descriptions-gongyi'));       
            await fetchDataRenderFrame(partDesc);
            const childrens = modal.querySelectorAll(`[id^="subgongyi-"]`)
            childrens.forEach(children =>{ children.remove()})
        }
    }
    static hideContainSwitch(button, modal) {
        button = button.nodeName === 'BUTTON' ? button : button.parentNode;
        const icon = button.querySelector('#collapseIcon');
        const btnText = button.querySelector('span');
        const gongyiExtra = modal.querySelector('#parts-descriptions-gongyi .el-descriptions__extra');
        const gongyiBody = modal.querySelector('#parts-descriptions-gongyi .el-descriptions__body');
        const gongyiFooter = modal.querySelector('#parts-descriptions-gongyi .el-descriptions__footer');
        const subgongyiDesc = modal.querySelector('#parts-descriptions-subgongyi'); 

        if (button.classList.contains('content-hide')) {
            button.classList.remove('content-hide');
            icon.classList.replace('fa-chevron-down', 'fa-chevron-up');
            btnText.textContent = '收起内容';
            gongyiExtra && (gongyiExtra.style.display = 'block');
            gongyiBody && (gongyiBody.style.display = 'block');
            gongyiFooter && (gongyiFooter.style.display = 'block');
            subgongyiDesc && (subgongyiDesc.style.display = 'block');
        } else {
            button.classList.add('content-hide');
            icon.classList.replace('fa-chevron-up', 'fa-chevron-down');
            btnText.textContent = '展开内容';
            gongyiExtra && (gongyiExtra.style.display = 'none');
            gongyiBody && (gongyiBody.style.display = 'none');
            gongyiFooter && (gongyiFooter.style.display = 'none');
            subgongyiDesc && (subgongyiDesc.style.display = 'none');
        }
    }

}
export class ProcessEditer{
    constructor(modal) {
        this.modal = modal;
        this.selecter = modal.querySelector('#select-step-group');
        this.remarkBody = modal.querySelector('#remark');
        this.paramTable = modal.querySelector('#param-table');
        this.paramTbody = modal.querySelector('#param-table tbody');
        this.beforeTsf = modal.querySelector('.el-dialog__body .transfer-container #step-before-select #available-steps');
        this.afterTsf = modal.querySelector('.el-dialog__body .transfer-container #step-after-select #selected-steps');
        this.SeqNum = modal.dataset.SeqNum;
        this.orderPart = JSON.parse(modal.dataset.orderPart || '{}');
        const tableId = `process-${this.orderPart["FModel"]||''}`;   
        this.partDesc = document.querySelector(`#${tableId}`).closest(".el-descriptions")
        this.group = this.selecter.value;
        this.paramRender = new tableRenderer(this.paramTable)   
    }

    initModel()
    {
        this.paramTable && (this.paramTable.innerHTML = '');
        this.afterTsf && (this.afterTsf.innerHTML = '');
        this.remarkBody && (this.remarkBody.value = '');
        this.paramRender.createHeader();
        this.paramRender.data = []
        this.paramRender.createBody();
    }

    async setpsOptionLoad()
    {
        this.initModel();
        this.group = this.selecter.value;
        let param = { url: JSON.stringify(API_CONFIG['pmcui-porder']['step_transfer']['Other']), 
            url_params : JSON.stringify({EqpName : this.selecter.value})}
        if (this.group === '中间件')  param = { 
            url: JSON.stringify(API_CONFIG['pmcui-porder']['step_transfer']['中间件']), 
            url_params : JSON.stringify({FId : this.orderPart["FId"]})}
        utils.setDataset(this.beforeTsf, param)
        const transferRender = new transferRenderer(this.beforeTsf)
        await fetchDataRenderFrame(transferRender);
        this.paramTbody.innerHTML = ''

    }

    stepRemove(target)
    {
        this.afterTsf.removeChild(target);
        if (!this.paramTbody) return;
        const uuid = target.dataset.uuid;
        const row = this.paramTbody.querySelector(`tr[data-uuid="${uuid}"]`);
        if (row) this.paramTbody.removeChild(row);
    }

    stepAdd(target)
    {
        const stepDB = utils.datasetToObj(target)
        stepDB.uuid = Date.now().toString() + Math.random().toString(36).slice(2)

        const div = document.createElement('div');
        div.className = 'after-step-item';
        div.textContent = stepDB.Name;
        utils.setDataset(div, stepDB)
        this.afterTsf.appendChild(div);

        const tr = this.paramRender.createRow(stepDB);
        tr.dataset.uuid = stepDB.uuid
        this.paramTbody.appendChild(tr)
    }
    stepsSubmit()
    {
        const data = {
            ...this.orderPart,
            SeqNum: this.SeqNum,
            Description: this.remarkBody?.value || '',
            Steps_Step_EqpType_Name: this.group,
            Steps_Step_Id: [...this.afterTsf.querySelectorAll('.after-step-item')]
            .map(step => step.dataset.Id),
            Steps_Step_Name: [...this.afterTsf.querySelectorAll('.after-step-item')]
            .map(step => step.dataset.Name),
            Process_Steps_Parm: [...this.paramTbody.querySelectorAll('input')]
            .map(input => input.value || input.textContent)
        }; 
        const isCreate = this.modal.dataset.mode == 'create' ? true : false;
        const result = !this.partDesc? alert(`页面丢失重新点击添加工序`)||true : 
        data.Steps_Step_Id.length == 0? alert(`请选择适合工序`)||false :
            isCreate? new ProcRouteEditer(this.partDesc).newProcess(data)||true :
            new ProcRouteEditer(this.partDesc).editProcess(data, this.SeqNum)|| true
        return result
    }
}

function bindInputsForFilter(container, table) {
    let detail = [];
    let params = {};
    const orderId = container.dataset.filterOrderId;
    table.dataset.groupkey = 'POrder_id';
    if (orderId) {
        detail.push(`订单号: ${orderId}`);
        params['OrderId'] = orderId;        
        table.dataset.groupkey = '';}
    filter_inputs.forEach(key => {
        const val = container.querySelector('input[name="' + key + '"]').value.trim();
        if (val) {
            detail.push(`${key}: ${val}`);
            params[key] = val;}
    })                
    document.getElementById('filter-detail-content').textContent = detail.length ? detail.join('，') : '无';
    return params
}

function getSelectedCellValue(ids, selected) {
    let tr = selected.closest('tr');
    if (!tr || tr.parentNode.tagName.toLowerCase() !== 'tbody') return null;
    let result ={}
    ids.forEach(id => {
        const key = tr.children[id].getAttribute('data-key').split('.').at(-1);
        result[key] = tr.children[id].textContent.trim();
    });
    return result;
}

function renderPartDetailModalFrame(order_part, modal){
    const titleTextDiv = modal.querySelector('#parts-detail-modal-title');
    titleTextDiv.textContent = `${order_part['FModel']}  ${order_part['FName']}`;
    titleTextDiv.setAttribute('title', `${order_part['FModel']}  ${order_part['FName']}`);
    modal.dataset.orderPart = JSON.stringify(order_part);

    const childrens = modal.querySelectorAll(`[id^="parts-descriptions-"]`)
    childrens.forEach(children =>{
        const title = children.getAttribute('data-title');
        if (title != '') {       
            const partDesc = new partDescriptions(children);    
            partDesc.url = API_CONFIG['pmcui-porder'][title].path;
            partDesc.url_params = URLConfig.buildApiParams('pmcui-porder',title, order_part);
            fetchDataRenderFrame(partDesc);
        }else{
            renderSubgongyiFrame(children, 
                modal.querySelector('#parts-descriptions-gongyi .el-descriptions__extra select'));
        }
    })
}

function renderSubgongyiFrame(container, select)
{
    const endpoint = select.value;
    const param = endpoint==""? {url: '', endpoint: endpoint} : {
        url : JSON.stringify(API_CONFIG['pmcui-porder'].subPatrsMaterialLoad),
        endpoint : select.value
    }
    const subgongyiG = new subgongyiGroup(container, param, param.POrder_id);
    fetchDataRenderFrame(subgongyiG);
}

export function handleOrderPartFilterEvent(container, loadtable) {
    container.addEventListener('click', e => {
        if (e.target.matches('td')) {
            const orderId = getSelectedCellValue([0], e.target)
            container.dataset.filterOrderId = orderId['OrderId'];
            const url_parm = bindInputsForFilter(container, loadtable);
            loadtable.dataset.url_params = JSON.stringify(url_parm);
            renderTableAndLoadData(loadtable);
        };
        if (e.target.matches('#filter-confirm-btn')){
            const url_parm = bindInputsForFilter(container, loadtable);
            loadtable.dataset.url_params = JSON.stringify(url_parm);
            renderTableAndLoadData(loadtable);
        }
    })
}
export function handlePartsTableSelectEvent(container, modal) {
    container.addEventListener('click', e => {
        if (e.target.matches('td')) {
            const order_part = getSelectedCellValue([0,1,2,3,4], e.target)
            if (!order_part ) return;
            utils.switchOverlay(modal, true);
            renderPartDetailModalFrame(order_part, modal);}
    });
}
export function handlePartDetailModalEvent(modal) {
    modal.addEventListener('click', e => {
        if (e.target.matches('#switch-modal')) 
            utils.switchOverlay(modal, false);
        if (e.target.matches('#maximize-modal')) 
            utils.maximizeModal(modal, 'main');
        if (e.target.matches('#modal_edit')) 
            ProcRouteEditer.routeEditTriger(modal, e.target);
        if (e.target.matches('#row-remove')) {
            new ProcRouteEditer(e.target.closest(".el-descriptions")).deleteProcess();}
        if (e.target.matches('#new-process')){
            ProcRouteEditer.processEditTriger(e.target.closest(".el-descriptions").querySelector('.el-descriptions__body table'));}
        if (e.target.matches('#process_edit')){
            ProcRouteEditer.processEditTriger(
                e.target.closest(".el-descriptions").querySelector('.el-descriptions__body table'), e.target.closest("tr"));}
        if (e.target.matches('#table-save')) 
            new ProcRouteEditer(e.target.closest(".el-descriptions"), 'POST').update();
        if (e.target.matches('#selecter-save')) 
            ProcRouteEditer.selectedRouteSave(e.target.closest(".el-descriptions"));
        if (e.target.matches('select'))       
            new ProcRouteEditer(e.target.closest(".el-descriptions")).selectOptionLoad();
        if (e.target.matches('.collapse-btn') || e.target.parentNode.matches('.collapse-btn'))
            ProcRouteEditer.hideContainSwitch(e.target, modal);
    },300);

    modal.addEventListener('change', e => {
        if (e.target.matches('select')) {
            const partDesc = e.target.closest(".el-descriptions");
            new ProcRouteEditer(partDesc).selectedRouteLoad()}
    });
}
export function handleProcessEditModalEvent(modal)
{
    modal.addEventListener('change', e => {
        if (e.target.matches('#select-step-group')) new ProcessEditer(modal).setpsOptionLoad();
    });
    modal.addEventListener('click', e => {
        if (e.target.matches('.step-item')) new ProcessEditer(modal).stepAdd(e.target)
        if (e.target.matches('.after-step-item')) new ProcessEditer(modal).stepRemove(e.target)
        if (e.target.matches('#load-step-design')) {
            if(new ProcessEditer(modal).stepsSubmit()) utils.switchOverlay(modal, false);}
        if (e.target.matches('#close-step-design-modal')) utils.switchOverlay(modal, false)
    })
}
