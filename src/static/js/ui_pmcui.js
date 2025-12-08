import {fetchDataRenderFrame, renderFrameAndLoadData, TablerHandler} from './eventAction.js';
import {utils } from './utils.js';
import {API_CONFIG} from './apiConfig.js';
import {selecterRenderer, tableRenderer, transferRenderer } from './renderFrame.js';

class ProcessEditer{
    constructor(modal, param) {
        this.modal = modal;
        this.selecter = modal.querySelector('#select-step-group');
        this.remarkBody = modal.querySelector('#remark');
        this.paramTable = modal.querySelector('#param-table');
        this.paramTbody = modal.querySelector('#param-table tbody');
        this.beforeTsf = modal.querySelector('.el-dialog__body .transfer-container #step-before-select #available-steps');
        this.afterTsf = modal.querySelector('.el-dialog__body .transfer-container #step-after-select #selected-steps');
        this.seqnum = modal.dataset.seqnum;
        this.dataParams = JSON.parse(modal.dataset.dataParams || '{}');
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
    modelActive(table, row = null)
    {
        const tbody = table.querySelector('tbody');
        utils.switchOverlay(this.modal, true);        
        this.modal.seqnum = row? row.rowIndex : tbody?.rows?.length + 1 || 1;
        this.modal.dataset.mode = row? 'edit' : 'create';
        this.modal.dataset.dataParams = table.dataset.dataParams;
        this.initModel();  
    }

    async setpsOptionLoad()
    {
        this.initModel();
        this.group = this.selecter.value;
        let param = { url: JSON.stringify(API_CONFIG['c_gongyi']['step_transfer']['stepList']), 
            url_params : JSON.stringify({type_name : this.selecter.value})}
        if (this.group === '中间件')  param = { 
            url: JSON.stringify(API_CONFIG['c_gongyi']['step_transfer']['中间件']), 
            url_params : JSON.stringify({material_id : this.dataParams.material_id, version: this.dataParams.version})}
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
            ...this.dataParams,
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
        const table = document.querySelector('.tab-pane .active').querySelector('table');
        data.steps_step_ids.length == 0? alert(`请选择适合工序`)||false :
            isCreate? new tableRenderer(table).renderNewRow(data)||true :
            new tableRenderer(table).updateRow(table.querySelectorAll('tbody tr')[Number(this.seqnum) - 1], data)|| true
        return result
    }
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
