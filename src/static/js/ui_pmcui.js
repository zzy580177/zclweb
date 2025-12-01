import {fetchDataRenderFrame, renderTableAndLoadData, TablerHandler} from './eventAction.js';
import {utils } from './utils.js';
import {API_CONFIG} from './apiConfig.js';
import {selecterRenderer, tableRenderer, transferRenderer } from './renderFrame.js';

import {partDescriptions, descriptionsTable, partLabsDescriptions} from './c_gongyi.js';




function updateSelecterSaveButtonState(container, routeEndPoint) {
    const button = container.querySelector('#selecter-save');
    if (!button) return;
    
    const isEnabled = routeEndPoint !== '';
    button.disabled = !isEnabled;
    
    button.className = isEnabled? 'el-button el-button--primary    el-button--small':'';
    button.style.cursor = isEnabled ? 'pointer' : 'not-allowed';
    
    if (!isEnabled) {
        button.replaceWith(button.cloneNode(true));
    }

    button.classList.toggle('active', isEnabled);
    button.classList.toggle('disabled', !isEnabled);
}

class ProcRouteEditer extends TablerHandler{
    constructor(container, method){
        super(container.querySelector('.el-descriptions__body table'), method);
        this.container = container;
        this.selecter = container.querySelector('.el-descriptions__extra select')
        this.selectHelp = container.querySelector('#select-help-note')
        this.target = this.table.querySelector('tbody')
        this.data_params = JSON.parse(this.table.dataset.data_params||'{}')
        this.selectHelpText = `订单: ${this.data_params.order_id||''} 确认加工`
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
        if(rowIdx !== undefined && rowIdx >= 1 && rowIdx <= rows.length) {
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
        const text = this.selecter.options[this.selecter.selectedIndex].textContent.trim();
        if (!routeId) return;
        this.table.dataset.endpoint = routeId;
        this.selectHelp.textContent = `${this.selectHelpText}${text} `
        updateSelecterSaveButtonState(this.container, this.table.dataset.endpoint)
        const tableRender = new descriptionsTable(this.table);
        await fetchDataRenderFrame(tableRender); 
        selecterRenderer.change(this.selecter);
        
        //const isSubPart = this.container.dataset['isSubPart']=='true'
        //if(isSubPart) return
        //renderSubgongyiFrame(document.querySelector('#parts-descriptions-subgongyi'), data_params);
    }
    static processEditTriger(table, row)
    {
        const tbody = table.querySelector('tbody');
        const modal = document.getElementById('process-design-modal');
        utils.switchOverlay(modal, true);        
        modal.dataset.url = table.dataset.orderPart;
        modal.dataset.data_params = table.dataset.data_params;
        modal.dataset.seqnum = row? row.rowIndex : tbody?.rows?.length + 1 || 1;
        modal.dataset.mode = row? 'edit' : 'create';
        const editer = new ProcessEditer(modal)
        editer.initModel();  
    }
    static async routeEditTriger(modal, button) {    

        if (button.classList.contains('btn-active')) {
            button.classList.remove('btn-active');
            partLabsDescriptions.toggleEditButtons(modal, false);
        }
        else{
            button.classList.toggle('btn-active', true);            
            partLabsDescriptions.toggleEditButtons(modal, true);

        }
    }
    static hideContainSwitch(button, modal) {
        button = button.nodeName === 'BUTTON' ? button : button.parentNode;
        const icon = button.querySelector('#collapseIcon');
        const btnText = button.querySelector('span');
        const parts_tabs = modal.querySelector('#parts-descriptions-gongyi .custom-tabs');

        if (button.classList.contains('content-hide')) {
            button.classList.remove('content-hide');
            icon.classList.replace('fa-chevron-down', 'fa-chevron-up');
            btnText.textContent = '收起内容';
            parts_tabs && (parts_tabs.style.display = 'block');
        } else {
            button.classList.add('content-hide');
            icon.classList.replace('fa-chevron-up', 'fa-chevron-down');
            btnText.textContent = '展开内容';
            parts_tabs && (parts_tabs.style.display = 'none');
            //subgongyiDesc && (subgongyiDesc.style.display = 'none');
        }
    }

}
class ProcessEditer{
    constructor(modal) {
        this.modal = modal;
        this.selecter = modal.querySelector('#select-step-group');
        this.remarkBody = modal.querySelector('#remark');
        this.paramTable = modal.querySelector('#param-table');
        this.paramTbody = modal.querySelector('#param-table tbody');
        this.beforeTsf = modal.querySelector('.el-dialog__body .transfer-container #step-before-select #available-steps');
        this.afterTsf = modal.querySelector('.el-dialog__body .transfer-container #step-after-select #selected-steps');
        this.seqnum = modal.dataset.seqnum;
        this.data_params = JSON.parse(modal.dataset.data_params || '{}');
        this.partDesc = document.querySelector(`#${this.data_params.material_model||''}.tab-pane`)
        this.group = this.selecter.value;
        this.paramRender = new tableRenderer(this.paramTable)   
        this.paramRender.setMinRows(0)
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
        let param = { url: JSON.stringify(API_CONFIG['c_gongyi']['step_transfer']['stepList']), 
            url_params : JSON.stringify({type_name : this.selecter.value})}
        if (this.group === '中间件')  param = { 
            url: JSON.stringify(API_CONFIG['c_gongyi']['step_transfer']['中间件']), 
            url_params : JSON.stringify({material_id : this.data_params["material_id"], version: this.data_params["version"]})}
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
        div.textContent = stepDB.name;
        utils.setDataset(div, stepDB)
        this.afterTsf.appendChild(div);

        const tr = this.paramRender.createRow(stepDB);
        tr.dataset.uuid = stepDB.uuid
        this.paramTbody.appendChild(tr)
    }
    stepsSubmit()
    {
        const data = {
            ...this.data_params,
            seqnum: this.seqnum,
            description: this.remarkBody?.value || '',
            type_name: this.group,
            steps_step_ids: [...this.afterTsf.querySelectorAll('.after-step-item')]
            .map(step => step.dataset.id),
            steps_step_names: [...this.afterTsf.querySelectorAll('.after-step-item')]
            .map(step => step.dataset.name),
            steps_parms: [...this.paramTbody.querySelectorAll('input')]
            .map(input => input.value || input.textContent)
        }; 
        const isCreate = this.modal.dataset.mode == 'create' ? true : false;
        const result = !this.partDesc? alert(`页面丢失重新点击添加工序`)||true : 
        data.steps_step_ids.length == 0? alert(`请选择适合工序`)||false :
            isCreate? new ProcRouteEditer(this.partDesc).newProcess(data)||true :
            new ProcRouteEditer(this.partDesc).editProcess(data, this.seqnum)|| true
        return result
    }
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
            new ProcRouteEditer(e.target.closest(".tab-pane")).deleteProcess();}
        if (e.target.matches('#new-process')){
            ProcRouteEditer.processEditTriger(e.target.closest(".tab-pane").querySelector('.el-descriptions__body table'));}
        if (e.target.matches('#process_edit')){
            ProcRouteEditer.processEditTriger(
                e.target.closest(".tab-pane").querySelector('.el-descriptions__body table'), e.target.closest("tr"));}
        if (e.target.matches('#table-save')) 
            new ProcRouteEditer(e.target.closest(".tab-pane"), 'POST').update();
        if (e.target.matches('#selecter-save')) 
            ProcRouteEditer.selectedRouteSave(e.target.closest(".tab-pane"));
        if (e.target.matches('select'))       
            new ProcRouteEditer(e.target.closest(".tab-pane")).selectOptionLoad();
        if (e.target.matches('.collapse-btn') || e.target.parentNode.matches('.collapse-btn'))
            ProcRouteEditer.hideContainSwitch(e.target, modal);
        if(e.target.matches('.tab-item'))
        {
            const container = e.target.closest('.custom-tabs');
            const target = container.querySelector('.tab-item.active');
            target.classList.remove('active');
            e.target.classList.add('active');
            const tabPane = container.querySelector('.tab-pane.active');
            tabPane.classList.remove('active');
            const tabContentId = e.target.id;    
            const tabContentEl = document.querySelector(`#${tabContentId}.tab-pane`);
            tabContentEl.classList.add('active');   
        }
    },300);

    modal.addEventListener('change', e => {
        if (e.target.matches('select')) {
            const partDesc = e.target.closest(".tab-pane");
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
