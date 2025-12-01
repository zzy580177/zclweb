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
        if (!button || !button.parentNode) return;
        button = button.nodeName === 'BUTTON' ? button : button.parentNode;
        const icon = button.querySelector('#collapseIcon');
        const btnText = button.querySelector('span');
        const parts_tabs = modal.querySelector('.custom-tabs');

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
        const id_context = this.data_params.isCNC? `${this.data_params.material_model}-CNC` : this.data_params.material_model
        this.partDesc = document.querySelector(`#${id_context}.tab-pane`)
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
class CNCDesignModal{
    constructor(data_params) {
        this.data_params = data_params;
    }

    static showCNCDesignModal(data_params) {
        const modal = document.getElementById('cnc-design-modal');
        const overlay = document.getElementById('cnc-design-modal-overlay');

        // 填充基础信息并存储在模态框的数据属性中
        modal.dataset.orderId = data_params.order_id || '';
        modal.dataset.materialId = data_params.material_id || '';
        modal.dataset.materialNumber = data_params.material_number || '';
        modal.dataset.materialModel = data_params.material_model || '';
        modal.dataset.version = data_params.version || '';

        document.getElementById('cnc-order-id').textContent = data_params.order_id || '';
        document.getElementById('cnc-material-number').textContent = data_params.material_number || '';
        document.getElementById('cnc-material-model').textContent = data_params.material_model || '';
        document.getElementById('cnc-version').textContent = data_params.version || '';

        // 清空之前的工序卡
        document.getElementById('cnc-processes-container').innerHTML = '';

        // 显示模态框
        utils.switchOverlay(modal, true);
        utils.switchOverlay(overlay, true);
    }

    static addCNCProcessCard() {
        const container = document.getElementById('cnc-processes-container');
        const processCount = container.children.length + 1;

        const processCard = document.createElement('div');
        processCard.className = 'cnc-process-card';
        processCard.innerHTML = `
            <div class="cnc-process-header">
                <h4>CNC工序 ${processCount}</h4>
                <button class="el-button el-button--danger el-button--mini remove-process">删除</button>
            </div>
            <div class="cnc-process-body">
                <div style="margin-bottom: 10px;">
                    <label>工序描述：</label>
                    <input type="text" class="el-input__inner process-description" placeholder="请输入工序描述">
                </div>
                <div style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <label>工步列表：</label>
                        <div>
                            <button class="el-button el-button--info el-button--mini toggle-steps" data-expanded="true">
                                <i class="fa fa-chevron-down"></i> 收起
                            </button>
                            <button class="el-button el-button--primary el-button--mini add-step">添加工步</button>
                        </div>
                    </div>
                    <div class="steps-container">
                        <!-- 工步将动态添加在这里 -->
                    </div>
                </div>
            </div>
        `;

        container.appendChild(processCard);
    }

    static async loadStepOptions(selectElement) {
        const selecterRender = new selecterRenderer(selectElement)
        selecterRender.url = API_CONFIG['c_gongyi']['step_transfer']['stepList'];
        selecterRender.url_params = {type_name : 'CNC 工步'}
        await fetchDataRenderFrame(selecterRender)
    }

    static addCNCStep(processCard) {
        const stepsContainer = processCard.querySelector('.steps-container');
        const stepCount = stepsContainer.children.length + 1;

        const stepItem = document.createElement('div');
        stepItem.className = 'cnc-step-item';
        stepItem.innerHTML = `
            <div class="cnc-step-number">${stepCount}</div>
            <div class="cnc-step-content">
                <div style="margin-bottom: 8px;">
                    <select class="el-select__inner step-select" id="cnc-step-select" data-key="id" data-text-k="name" style="width: 100%;">
                        <option value="">选择工步</option>
                    </select>
                </div>
                <div class="cnc-machining-params">
                    <div class="cnc-machining-param-item">
                        <label>刀具名称</label>
                        <input type="text" class="el-input__inner tool-name" placeholder="输入刀具名称">
                    </div>
                    <div class="cnc-machining-param-item">
                        <label>直径(mm)</label>
                        <input type="number" step="0.01" class="el-input__inner tool-diameter" placeholder="刀具直径">
                    </div>
                    <div class="cnc-machining-param-item">
                        <label>长度(mm)</label>
                        <input type="number" step="0.01" class="el-input__inner tool-length" placeholder="刀具长度">
                    </div>
                    <div class="cnc-machining-param-item">
                        <label>切削速度(m/min)</label>
                        <input type="number" step="0.1" class="el-input__inner cutting-speed" placeholder="切削速度">
                    </div>
                    <div class="cnc-machining-param-item">
                        <label>主轴转速(rpm)</label>
                        <input type="number" class="el-input__inner spindle-speed" placeholder="主轴转速">
                    </div>
                    <div class="cnc-machining-param-item">
                        <label>进给量(mm/min)</label>
                        <input type="number" step="0.1" class="el-input__inner feed-rate" placeholder="进给量">
                    </div>
                    <div class="cnc-machining-param-item">
                        <label>对刀位置</label>
                        <input type="text" class="el-input__inner tool-position" placeholder="对刀位置">
                    </div>
                    <div class="cnc-machining-param-item">
                        <label>分中位置</label>
                        <input type="text" class="el-input__inner center-position" placeholder="分中位置">
                    </div>
                </div>
            </div>
            <div class="cnc-step-actions">
                <button class="el-button el-button--danger el-button--mini remove-step">删除</button>
            </div>
        `;

        stepsContainer.appendChild(stepItem);
        CNCDesignModal.loadStepOptions(stepItem.querySelector('#cnc-step-select'));
    }

    static updateProcessNumbers() {
        const processCards = document.querySelectorAll('.cnc-process-card');
        processCards.forEach((card, index) => {
            card.querySelector('h4').textContent = `CNC工序 ${index + 1}`;
        });
    }

    static updateStepNumbers(processCard) {
        const stepItems = processCard.querySelectorAll('.cnc-step-item');
        stepItems.forEach((item, index) => {
            item.querySelector('.cnc-step-number').textContent = index + 1;
        });
    }

    static async saveCNCDesign() {
        const saveData = CNCDesignModal.getData();
        if (!saveData) return;
        //await renderTableAndLoadData(this.table, this.method, this.data, true, descriptionsTable)
        try {
            const response = await fetch('/api/c_gongyi/cnc_process/cnc_route', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify(saveData)
            });

            const result = await response.json();

            if (result.route_id && result.route_id !== 0) {
                alert(result.message || '保存成功');
                // 关闭模态框
                utils.switchOverlay(document.getElementById('cnc-design-modal'), false);
                utils.switchOverlay(document.getElementById('cnc-design-modal-overlay'), false);

                // 刷新工艺设计区域
                CNCDesignModal.refreshCNCTable();
            } else {
                alert(result.message || '保存失败');
            }
        } catch (error) {
            console.error('保存失败:', error);
            alert('保存失败，请重试');
        }
    }

    static getData() {
        const processesData = [];
        const processCards = document.querySelectorAll('.cnc-process-card');

        if (processCards.length === 0) {
            alert('请至少添加一个CNC工序');
            return null;
        }

        for (let i = 0; i < processCards.length; i++) {
            const card = processCards[i];
            const description = card.querySelector('.process-description').value.trim();
            const stepItems = card.querySelectorAll('.cnc-step-item');

            if (stepItems.length === 0) {
                alert(`CNC工序 ${i + 1} 至少需要一个工步`);
                return null;
            }

            const steps = [];
            const stepParams = [];

            stepItems.forEach(stepItem => {
                const stepSelect = stepItem.querySelector('#cnc-step-select');

                if (!stepSelect.value) {
                    alert('请选择工步');
                    return null;
                }

                // 收集详细的工艺参数
                const machiningParams = {
                    tool_name: stepItem.querySelector('.tool-name').value.trim(),
                    tool_diameter: parseFloat(stepItem.querySelector('.tool-diameter').value) || 0,
                    tool_length: parseFloat(stepItem.querySelector('.tool-length').value) || 0,
                    cutting_speed: parseFloat(stepItem.querySelector('.cutting-speed').value) || 0,
                    spindle_speed: parseFloat(stepItem.querySelector('.spindle-speed').value) || 0,
                    feed_rate: parseFloat(stepItem.querySelector('.feed-rate').value) || 0,
                    tool_position: stepItem.querySelector('.tool-position').value.trim(),
                    center_position: stepItem.querySelector('.center-position').value.trim()
                };

                steps.push(stepSelect.value);
                stepParams.push(machiningParams);
            });

            processesData.push({
                seqnum: i + 1,
                description: description,
                steps_step_ids: steps,
                steps_parms: stepParams,
                params: {}
            });
        }
        const modal = document.getElementById('cnc-design-modal');
        return {
            material_id: parseInt(modal.dataset.materialId),
            version: modal.dataset.version,
            order_id: modal.dataset.orderId,
            cnc_processes: processesData
        };
    }

    static refreshCNCTable() {
        // 找到对应的CNC工艺设计容器并刷新
        const cncContainer = document.querySelector('#parts-descriptions-cnc-gongyi');
        if (cncContainer) {
            const selecter = cncContainer.querySelector('select');
            if (selecter) {
                selecter.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }
    }

    static async loadExistingCNCDesign(routeId, data_params) {
        try {
            const response = await fetch(`/api/c_gongyi/cnc_process/route/${routeId}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }   
            const result = await response.json();
            const cncProcesses = result.data
            console.log('API response:', cncProcesses);

            if (!Array.isArray(cncProcesses) || cncProcesses.length === 0) {
                alert('该工艺线路没有CNC工序数据');
                return;
            }

            // 显示模态框并填充基础信息
            CNCDesignModal.showCNCDesignModal(data_params);

            // 遍历CNC工序数据，创建工序卡片
            cncProcesses.forEach((cncProcess, index) => {
                // 添加工序卡片
                CNCDesignModal.addCNCProcessCard();

                // 获取刚添加的工序卡片
                const processCards = document.querySelectorAll('.cnc-process-card');
                const currentCard = processCards[processCards.length - 1];

                // 填充工序描述
                const descriptionInput = currentCard.querySelector('.process-description');
                if (descriptionInput && cncProcess.description) {
                    descriptionInput.value = cncProcess.description;
                }

                // 获取工步数据（假设工步信息在 params 或其他字段中）
                const steps = cncProcess.steps || [];
                const stepsContainer = currentCard.querySelector('.steps-container');

                if (steps.length === 0 && cncProcess.steps_step_ids && cncProcess.steps_parms) {
                    // 从步骤ID和参数构建工步数据
                    const stepIds = Array.isArray(cncProcess.steps_step_ids) ? cncProcess.steps_step_ids : [];
                    const stepParms = Array.isArray(cncProcess.steps_parms) ? cncProcess.steps_parms : [];

                    stepIds.forEach((stepId, stepIndex) => {
                        // 添加工步
                        CNCDesignModal.addCNCStep(currentCard);

                        // 获取刚添加的工步项
                        const stepItems = currentCard.querySelectorAll('.cnc-step-item');
                        const currentStep = stepItems[stepItems.length - 1];

                        // 设置工步选择
                        const stepSelect = currentStep.querySelector('#cnc-step-select');
                        if (stepSelect) {
                            stepSelect.value = stepId;
                        }

                        // 填充工艺参数
                        const stepParams = stepParms[stepIndex] || {};
                        const inputs = currentStep.querySelectorAll('input, select');
                        inputs.forEach(input => {
                            const fieldName = input.className.replace('el-input__inner ', '');
                            if (stepParams[fieldName]) {
                                if (input.type === 'number') {
                                    input.value = parseFloat(stepParams[fieldName]) || 0;
                                } else {
                                    input.value = stepParams[fieldName];
                                }
                            }
                        });
                    });
                } else {
                    // 处理标准工步格式
                    steps.forEach(step => {
                        CNCDesignModal.addCNCStep(currentCard);

                        const stepItems = currentCard.querySelectorAll('.cnc-step-item');
                        const currentStep = stepItems[stepItems.length - 1];

                        // 设置工步信息（根据实际API返回的数据结构调整）
                        const stepSelect = currentStep.querySelector('#cnc-step-select');
                        if (stepSelect && step.id) {
                            stepSelect.value = step.id;
                        }

                        // 填充参数（根据实际数据结构调整）
                        if (step.params) {
                            const inputs = currentStep.querySelectorAll('input');
                            inputs.forEach(input => {
                                const fieldName = input.className.replace('el-input__inner ', '');
                                if (step.params[fieldName]) {
                                    if (input.type === 'number') {
                                        input.value = parseFloat(step.params[fieldName]) || 0;
                                    } else {
                                        input.value = step.params[fieldName];
                                    }
                                }
                            });
                        }
                    });
                }

                // 更新工序编号和工步编号
                CNCDesignModal.updateStepNumbers(currentCard);
            });

            // 更新所有工序编号
            CNCDesignModal.updateProcessNumbers();

        } catch (error) {
            console.error('加载CNC设计失败:', error);
            alert('加载现有CNC工序设计失败，请重试');
        }
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
        if (e.target.matches('.collapse-btn') || e.target.parentNode.matches('.collapse-btn')){
            const container = e.target.closest('.el-descriptions');
            ProcRouteEditer.hideContainSwitch(e.target, container);
        }
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
        if (e.target.matches('#new-route')) {
            e.preventDefault();
            const table = e.target.closest('.tab-pane.active').querySelector('table')
            const data_params = JSON.parse(table.dataset.data_params)
            CNCDesignModal.showCNCDesignModal(data_params);
        }
        if (e.target.matches('#compile-existing')) {
            e.preventDefault();
            const tabPane = e.target.closest('.tab-pane.active');
            const selector = tabPane.querySelector('select');
            const routeId = selector?.value;

            if (!routeId) {
                alert('请先选择一个历史工艺线路');
                return;
            }

            // 获取物料信息
            const table = tabPane.querySelector('table');
            const data_params = JSON.parse(table?.dataset.data_params || '{}');

            // 加载已有的CNC设计
            CNCDesignModal.loadExistingCNCDesign(routeId, data_params);
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
export function handleCNCDesignModalEvent(modal)
{
    modal.addEventListener('click', e => {

        if (e.target.matches('.toggle-steps') || e.target.closest('.toggle-steps')) {
            const button = e.target.closest('.toggle-steps');
            const processCard = button.closest('.cnc-process-card');
            const stepsContainer = processCard.querySelector('.steps-container');

            const isExpanded = button.dataset.expanded === 'true';

            if (isExpanded) {
                // 收起
                button.innerHTML = '<i class="fa fa-chevron-right"></i> 展开';
                button.dataset.expanded = 'false';
                stepsContainer.style.display = 'none';
            } else {
                // 展开
                button.innerHTML = '<i class="fa fa-chevron-down"></i> 收起';
                button.dataset.expanded = 'true';
                stepsContainer.style.display = 'block';
            }
        }

        if (e.target.matches('.remove-process')) {
            const processCard = e.target.closest('.cnc-process-card');
            processCard.remove();
            CNCDesignModal.updateProcessNumbers();
        }
        if (e.target.matches('.remove-step')) {
            const processCard = e.target.closest('.cnc-process-card');
            if (!processCard) {
                console.error('Error: Could not find the parent .cnc-process-card element.');
                return;
            }
            const stepItem = e.target.closest('.cnc-step-item');
            if (!stepItem) {
                console.error('Error: Could not find the .cnc-step-item element to remove.');
                return;
            }
            stepItem.remove();
            CNCDesignModal.updateStepNumbers(processCard);
        }
        if (e.target.matches('.add-step'))
            CNCDesignModal.addCNCStep(e.target.closest('.cnc-process-card'));
        if (e.target.matches('#save-cnc-design'))
            CNCDesignModal.saveCNCDesign()
        if (e.target.matches('#add-cnc-process'))
            CNCDesignModal.addCNCProcessCard()
        if (e.target.matches('#switch-modal'))
            utils.switchOverlay(modal, false);
        if (e.target.matches('#maximize-modal'))
            utils.maximizeModal(modal, '.el-dialog__body');
        if (e.target.matches('#cancel-cnc-design')) utils.switchOverlay(modal, false)
    })
}
