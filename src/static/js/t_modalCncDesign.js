import { utils, URLConfig } from './utils.js';
import {fetchDataRenderFrame} from './eventAction.js';
import { API_CONFIG } from './apiConfig.js';
import { selecterRenderer } from './renderFrame.js';

// 常量定义
const MODAL_IDS = {
    MODAL: 'cnc-design-modal',
    OVERLAY: 'cnc-design-modal-overlay',
    CONTAINER: 'cnc-processes-container',
    ORDER_ID: 'cnc-order-id',
    MATERIAL_NUMBER: 'cnc-material-number',
    MATERIAL_MODEL: 'cnc-material-model',
    PART_VERSION: 'cnc-part-version',
    PROCESS_VERSION: 'cnc-process-version'
};

// 数字类型单位关键词
export const NUMERIC_UNITS = ['mm', 'rpm', 'min'];

export class CNCDesignModal{
    static stepOptionsCache = new Map();       // 存放API数据，键为type_name
    static stepOptionsPromise = new Map();     // 存放Promise，键为type_name
   
    async loadStepOptionsCached(typeName = null) {
        // 确定type_name，优先使用传入的参数，否则使用当前selecter_url.params.type_name
        const currentTypeName = typeName || (this.selecter_url.params && this.selecter_url.params.type_name) || 'CNC';
        const cacheKey = currentTypeName;
        
        // 检查缓存
        if (CNCDesignModal.stepOptionsCache.has(cacheKey)) {
            return CNCDesignModal.stepOptionsCache.get(cacheKey);
        }
        
        // 检查是否有正在进行的请求
        if (CNCDesignModal.stepOptionsPromise.has(cacheKey)) {
            return await CNCDesignModal.stepOptionsPromise.get(cacheKey);
        }
        
        // 创建新的请求Promise
        const promise = new Promise(async (resolve, reject) => {
            // 临时保存原始的selecter_url.params
            const originalParams = {...this.selecter_url.params};
            
            // 设置请求参数
            this.selecter_url.params = { type_name: currentTypeName };
            
            fetchDataRenderFrame({
                url: this.selecter_url,
                method: 'GET',
                render: (response) => {
                    // 处理响应格式：response 可能是 {success: true, data: [...]} 或直接是数组
                    let options = [];
                    if (response) {
                        if (Array.isArray(response)) {
                            // 直接返回数组的情况
                            options = response;
                        } else if (response.success !== false && Array.isArray(response.data)) {
                            // 标准格式：{success: true, data: [...]}
                            options = response.data;
                        } else if (Array.isArray(response.data)) {
                            // 即使 success=false，也可能有数据
                            options = response.data;
                        }
                    }
                    CNCDesignModal.stepOptionsCache.set(cacheKey, options);
                    resolve(options);
                },
                renderError: (error) => {
                    console.info(`获取Step选项错误 (type_name: ${currentTypeName}):`, error);
                    CNCDesignModal.stepOptionsCache.set(cacheKey, []);
                    resolve([]);
                },
                toggleLoad: false
            });
            
            // 恢复原始的selecter_url.params
            this.selecter_url.params = originalParams;
        });
        
        CNCDesignModal.stepOptionsPromise.set(cacheKey, promise);
        
        try {
            const result = await promise;
            return result;
        } finally {
            // 请求完成后清理Promise缓存
            CNCDesignModal.stepOptionsPromise.delete(cacheKey);
        }
    }
    
    async loadStepOptions(selectElement, selectedValue = null, typeName = null) {
        try {
            const options = await this.loadStepOptionsCached(typeName);
            const renderer = new selecterRenderer(selectElement);
            renderer.option = {key:"id",textK:"name"}
            renderer.render(options);
            if (selectedValue) {
                renderer.updateSelected(selectedValue);
            }
        } catch (error) {
            console.error('加载工步选项失败:', error);
            // 渲染空选项，避免界面卡死
            const renderer = new selecterRenderer(selectElement);
            renderer.render([]);
            throw error;
        }
    }

    
    async getAvailableStepOptions() {
        return await this.loadStepOptionsCached();
    }

    constructor(dataParams = null, StepParam = null, method = null, type = 'NEW') {
        this.modal = document.getElementById(MODAL_IDS.MODAL);
        this.container = document.getElementById(MODAL_IDS.CONTAINER);

        // 更安全的参数处理
        if (dataParams) {
            this.dataParams = dataParams;
            this.modal.dataset.dataParams = JSON.stringify(dataParams);
        } else if (this.modal?.dataset?.dataParams) {
            try {
                this.dataParams = JSON.parse(this.modal.dataset.dataParams);
            } catch (e) {
                console.info('Invalid dataParams in modal dataset:', e);
                this.dataParams = {};
            }
        } else {
            this.dataParams = {};
        }
        this.type = type ? type : this.modal.dataset.type || '';
        this.url = API_CONFIG['c_gongyi']['工艺线路'].path;
        this.url.params = URLConfig.buildApiParams(API_CONFIG['c_gongyi']['工艺线路'], this.dataParams);
        this.endpoint = this.dataParams.route;
        
        // 安全地处理 StepParam，防止 null 或 undefined
        const safeStepParam = StepParam || {};
        const stepParams = safeStepParam['Params'] || {};
        const stepEQP = safeStepParam['EQP'] || {};
        
        this.crafParams = this.dataParams.isCNC ? stepParams['CNC'] || [] : stepParams['UNCNC'] || [];
        this.eqpTyp = this.dataParams.isCNC ? stepEQP['CNC'] || [] : stepEQP['UNCNC'] || [];
        this.method = method;
        this.selecter_url = {path: API_CONFIG['c_gongyi']['step_transfer']['stepList'], params: {type_name : 'CNC'}};
    }

    setType(type) {
        this.type = type;
        this.modal.dataset.type = type;
    }

    setActiveLab(tabId) {
        this.modal.dataset.tabId = tabId;

    }

    initialDesignModal() {
        document.getElementById(MODAL_IDS.ORDER_ID).textContent = this.dataParams.order_id || '';
        document.getElementById(MODAL_IDS.MATERIAL_NUMBER).textContent = this.dataParams.material_number || '';
        document.getElementById(MODAL_IDS.MATERIAL_MODEL).textContent = this.dataParams.material_model || '';
        // 为两个版本字段设置相同的值
        const versionValue = this.dataParams.version || '';
        document.getElementById(MODAL_IDS.PART_VERSION).textContent = versionValue;
        document.getElementById(MODAL_IDS.PROCESS_VERSION).textContent = '';

        // 清空之前的工序卡
        document.getElementById(MODAL_IDS.CONTAINER).innerHTML = '';

        // 显示模态框
        utils.switchOverlay(this.modal, true);
    }

    validateFormInputs(target) {
        if (!target)  return true;
        const requiredFields = target.querySelectorAll('input[required], select[required]');
        requiredFields.forEach(element => {element.classList.remove('unvalid');});
        const invalidEl = [];
        requiredFields.forEach(element => { if (!element.checkValidity()) {
            element.classList.add('unvalid');
            invalidEl.push(element);
        }});
        return invalidEl.length === 0;
    }
    
    addProcessCard(processData = null) {
        const processCount = this.container.children.length + 1;
        const processTitle = this.dataParams.isCNC ? 'CNC工序' : '工序';

        const processCard = document.createElement('div');
        processCard.className = 'cnc-process-card';
        
        // 创建设备选项HTML
        let deviceOptionsHtml = '<option value="">选择设备分类</option>';
        if (this.eqpTyp && Array.isArray(this.eqpTyp)) {
            this.eqpTyp.forEach(device => {
                if (device && device.value && device.label) {
                    deviceOptionsHtml += `<option value="${device.label}">${device.label}</option>`;
                }
            });
        }
        
        processCard.innerHTML = `
            <div class="cnc-process-header" style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background-color: #f5f7fa; border-bottom: 1px solid #e4e7ed;">
                <h4 style="margin: 0; font-size: 14px; font-weight: 600; color: #303133;">${processTitle} ${processCount}</h4>
                <button class="el-button el-button--danger el-button--mini remove-process" style="padding: 5px 10px; font-size: 12px;">删除</button>
            </div>
            <div class="cnc-process-body" style="padding: 12px;">
                <div style="display: flex; gap: 12px; margin-bottom: 12px;">
                    <div style="flex: 1;">
                        <label style="display: block; margin-bottom: 4px; font-size: 13px; color: #606266;">工序描述：</label>
                        <input type="text" class="el-input__inner process-description" placeholder="请输入工序描述" style="width: 100%; padding: 6px 10px; font-size: 13px; height: 32px;">
                    </div>
                    <div style="flex: 1;">
                        <label style="display: block; margin-bottom: 4px; font-size: 13px; color: #606266;">设备选择：</label>
                        <select class="el-input__inner device-select" style="width: 60%; padding: 0px 10px; font-size: 13px; height: 32px;"1, required>
                            ${deviceOptionsHtml}
                        </select>
                    </div>
                </div>
                <div style="margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <label style="font-size: 13px; color: #606266;">工步列表：</label>
                        <div>
                            <button class="el-button el-button--info el-button--mini toggle-steps" data-expanded="true" style="padding: 4px 8px; font-size: 12px; margin-right: 6px;">
                                <i class="fa fa-chevron-down" style="font-size: 12px;"></i> 收起
                            </button>
                            <button class="el-button el-button--primary el-button--mini add-step" style="padding: 4px 8px; font-size: 12px;">
                                添加工步
                            </button>
                        </div>
                    </div>
                    <div class="steps-container" style="border: 1px solid #e4e7ed; border-radius: 4px; padding: 8px;">
                        <!-- 工步将动态添加在这里 -->
                    </div>
                </div>
            </div>`;
        this.container.appendChild(processCard);

        // 填充数据如果提供
        if (processData && processData.description) {
            const descriptionInput = processCard.querySelector('.process-description');
            if (descriptionInput) {
                descriptionInput.value = processData.description;
            }
        }

        if (processData && processData.type_name) {
            const deviceSelect = processCard.querySelector('.device-select');
            if (deviceSelect) {
                const option = Array.from(deviceSelect.options).find(opt => opt.value === processData.type_name);
                if (option) {
                    option.selected = true;
                    deviceSelect.value = processData.type_name;
                }
            }
        }

        return processCard;
    }

    async addStep(processCard, stepData = null) {
        const type = processCard.querySelector('.device-select').value;
        this.selecter_url.params = this.dataParams.isCNC ? {type_name : 'CNC'} : {type_name : type}; 

        const stepsContainer = processCard.querySelector('.steps-container');
        const stepCount = stepsContainer.children.length + 1;
        const stepItem = document.createElement('div');
        stepItem.className = 'cnc-step-item';
        stepItem.innerHTML = `
            <div class="cnc-step-number">${stepCount}</div>
            <div class="cnc-step-content">
                <div style="margin-bottom: 8px;">
                    <select class="el-select__inner step-select" id="cnc-step-select" style="width: 40%;" required>
                        <option value="">选择工步</option>
                    </select>
                </div>
                <div class="cnc-machining-params">
                </div>
            </div>
            <div class="cnc-step-actions">
                <button class="el-button el-button--danger el-button--mini remove-step">删除</button>
            </div>
        `;
        stepsContainer.appendChild(stepItem);
        // 加载选项
        const stepSelect = stepItem.querySelector('#cnc-step-select');
        // 修复：传递正确的参数：selectElement, selectedValue, typeName
        const selectedValue = stepData ? stepData.step_id || stepData.id : null;
        const typeName = this.dataParams.isCNC ? 'CNC' : type;
        await this.loadStepOptions(stepSelect, selectedValue, typeName);

        let paramsInfo = stepData && stepData.params ? stepData.params : null;
        paramsInfo = typeof paramsInfo === 'string'? JSON.parse(paramsInfo) : paramsInfo;
        this.createParamsForm(stepItem, paramsInfo);
        return stepItem;
    }
    createParamsForm(stepItem, paramsInfo = null) {
        const paramsForm = document.createElement('div');
        const paramCount = this.crafParams.length;

        // 根据参数数量设置CSS类，实现响应式布局
        let layoutClass = 'param-count-default'; // 默认6个以上参数的情况
        if (paramCount === 1) {
            layoutClass = 'param-count-1';
        } else if (paramCount === 2) {
            layoutClass = 'param-count-2';
        } else if (paramCount === 3) {
            layoutClass = 'param-count-3';
        } else if (paramCount === 4) {
            layoutClass = 'param-count-4';
        } else if (paramCount >= 5 && paramCount <= 6) {
            layoutClass = 'param-count-5'; // 5-6个参数使用相同布局
        }

        paramsForm.className = `cnc-machining-params ${layoutClass}`;

        this.crafParams.forEach(param => {
            let paramItem = document.createElement('div');
            const type = NUMERIC_UNITS.some(keyword => param.label.includes(keyword)) ? 'number' : 'text';
            paramItem.className = 'cnc-machining-param-item';
            paramItem.innerHTML = `
                <label>${param.label}</label>
                <input type=${type} class="el-input__inner ${param.key}" placeholder="${param.label}">
            `;
            const input = paramItem.querySelector(`.${param.key}`);
            const value = paramsInfo && (paramsInfo[param.key] || paramsInfo[param.label])!== undefined ? paramsInfo[param.key]|| paramsInfo[param.label] : "";
            if (type === 'number') {
                input.value = parseFloat(value) || "";
            } else {
                input.value = value;
            }
            paramsForm.appendChild(paramItem);
        })
        stepItem.querySelector('.cnc-machining-params').appendChild(paramsForm);
    }

    static updateProcessNumbers() {
        const processCards = document.querySelectorAll('.cnc-process-card');
        processCards.forEach((card, index) => {
            card.querySelector('h4').textContent = `CNC工序 ${index + 1}`;
        });
        return processCards.length;
    }

    static updateStepNumbers(processCard) {
        const stepItems = processCard.querySelectorAll('.cnc-step-item');
        stepItems.forEach((item, index) => {
            item.querySelector('.cnc-step-number').textContent = index + 1;
        });
    }

    async handleFastFillDate(data) {
        if (!Array.isArray(data) || data.length === 0) {
            console.info('handleFastFillDate: 无效的数据格式或空数组');
            alert('没有找到需要添加的工步数据');
            return false;
        }

        CNCDesignModal.stepOptionsCache.delete('CNC');
        CNCDesignModal.stepOptionsPromise.delete('CNC');

        try {
            const validatedSteps = await this.validateAndConvertStepData(data);
            if (validatedSteps.length === 0) {
                alert('没有找到有效的工步数据，请检查输入格式');
                return false;
            }

            const processData = this.createProcessFromSteps(validatedSteps);
            this.loadAndRenderProcessCard(processData);

            CNCDesignModal.updateProcessNumbers();
            return true;

        } catch (error) {
            console.info('handleFastFillDate error:', error);
            alert(error.message || '数据处理失败，请检查输入格式');
            return false;
        }
    }

    async validateAndConvertStepData(rawData, typeName = 'CNC', processNo = null) {
        try {
            // 根据传入的typeName获取对应的工步列表
            const availableSteps = await this.loadStepOptionsCached(typeName);
            if (!availableSteps || availableSteps.length === 0) {
                throw new Error('无法获取可用的工步选项，请检查网络连接');
            }

            const expectedFields = ['step_name', ...this.crafParams.map(param => param.key)];
            const numericFields = this.crafParams
                .filter(param => NUMERIC_UNITS.some(keyword => param.label.includes(keyword)))
                .map(param => param.key);

            const validSteps = [];
            const errors = [];

            rawData.forEach((row, index) => {
                const rowNumber = processNo? processNo : index + 1;
                const rowErrors = [];

                const stepName = row.step_name;
                if (!stepName || stepName.trim() === '') {
                    rowErrors.push(`工步名称为空`);
                    return;
                }
                let matchedStep = null;
                if (stepName && stepName.trim()) {
                    matchedStep = this.findMatchingStep(stepName, availableSteps);
                    if (!matchedStep) {
                        rowErrors.push(`工步名称 "${stepName}" 不存在于可用选项中`);
                    }
                }
                for (const field of expectedFields) {
                    if (field !== 'step_name' && row.hasOwnProperty(field)) {
                        const value = row[field];
                        if (value !== null && value !== undefined && value !== '') {
                            if (numericFields.includes(field)) {
                                const numericValue = parseFloat(value);
                                if (isNaN(numericValue)) {
                                    rowErrors.push(`字段 "${field}" 的值为 "${value}"，不是有效数值`);
                                }
                            }
                        }
                    }
                }

                const actualFields = Object.keys(row);
                const extraFields = actualFields.filter(field => !expectedFields.includes(field));
                if (extraFields.length > 0) {
                    rowErrors.push(`发现未定义字段: ${extraFields.join(', ')}`);
                }

                if (rowErrors.length === 0 && matchedStep) {
                    const stepData = this.createStepDataFromRow(row, matchedStep);
                    validSteps.push(stepData);
                } else if (rowErrors.length > 0) {
                    const errorPrefix = `第 ${rowNumber} 行：`;
                    rowErrors.forEach(error => {
                        errors.push(errorPrefix + error);
                    });
                }
            });
            if (errors.length > 0) {
                throw new Error('数据验证失败：\n' + errors.join('\n'));
            }

            return validSteps;

        } catch (error) {
            console.info('validateAndConvertStepData error:', error);
            throw error;
        }
    }

    createStepDataFromRow(row, matchedStep = null) {
        const stepData = {
            step_id: matchedStep ? matchedStep.id : (row.step_name || row['工步名称'] || 'temp_step_id'),            
            step_name: matchedStep ? matchedStep.name : (row.step_name || row['工步名称'] || 'temp_step_name'),
            params: {}
        };

        if (this.crafParams && Array.isArray(this.crafParams)) {
            this.crafParams.forEach(param => {
                const key = param.key;
                if (row.hasOwnProperty(key)) {
                    let value = row[key];
                    if (NUMERIC_UNITS.some(keyword => param.label.includes(keyword))) {
                        value = parseFloat(value) || "";
                    } else {
                        value = (value || '').toString().trim();
                    }
                    stepData.params[key] = value;
                }
            });
        }

        return stepData;
    }

    findMatchingStep(stepName, availableSteps) {
        if (!availableSteps || !Array.isArray(availableSteps)) {
            return null;
        }
        const normalizedStepName = stepName.trim().toLowerCase();
        const exactMatch = availableSteps.find(step =>
            (step.name || '').trim().toLowerCase() === normalizedStepName
        );
        if (exactMatch) {
            return exactMatch;
        }
        return null;

        // 如果没有精确匹配，尝试模糊匹配（包含关系）
        //const fuzzyMatch = availableSteps.find(step =>
        //    normalizedStepName.includes((step.name || '').trim().toLowerCase()) ||
        //    (step.name || '').trim().toLowerCase().includes(normalizedStepName)
        //);

        //return fuzzyMatch || null;
    }
    createProcessFromSteps(validatedSteps, processItem = null) {
        const processData = {
            description: processItem? processItem.process_name : '快速添加工序', // 默认描述，可后续编辑
            seqnum: null,
            type_name: processItem? processItem.type_name : '', // 默认设备ID，可后续编辑
            steps: [],
            steps_step_ids: [],
            steps_step_names: [],
            steps_parms: [],
            params: {}
        };

        // 将所有工步添加到工序中
        validatedSteps.forEach(stepData => {
            processData.steps_step_names.push(stepData.step_name);
            processData.steps_step_ids.push(stepData.step_id);
            processData.steps_parms.push(stepData.params);
            processData.steps.push(Number(stepData.step_id));
        });

        return processData;
    }

    getData() {
        const processesData = [];
        const processCards = document.querySelectorAll('.cnc-process-card');

        if (processCards.length === 0) {
            alert('请至少添加一个CNC工序');
            return null;
        }

        for (let i = 0; i < processCards.length; i++) {
            const card = processCards[i];
            const description = card.querySelector('.process-description').value.trim();
            const deviceSelect = card.querySelector('.device-select');
            const type_name = deviceSelect ? deviceSelect.value : '';
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

                // 动态收集工艺参数
                const machiningParams = {};
                this.crafParams.forEach(param => {
                    const element = stepItem.querySelector(`.${param.key}`);
                    if (element) {
                        const value = element.value;
                        machiningParams[param.label] = NUMERIC_UNITS.some(keyword => param.label.includes(keyword)) ? parseFloat(value) || "" : value.trim();
                    }
                });

                steps.push(stepSelect.value);
                stepParams.push(machiningParams);
            });

            processesData.push({
                seqnum: i + 1,
                description: description,
                type_name: type_name,
                steps_step_ids: steps,
                steps_parms: stepParams,
                params: {}
            });
        }
        const modal = document.getElementById(MODAL_IDS.MODAL);
        return {
            material_id: parseInt(this.dataParams.material_id),
            version: this.dataParams.version,
            order_id: this.dataParams.order_id,
            is_cnc: this.dataParams.isCNC,
            processes: processesData
        };
    }

    render(result){
        if(this.method === 'GET'){
            this.loadExistingDesign(result.data);
        }else{
            alert(result.message || '保存成功');
            utils.switchOverlay(this.modal, false);
            //utils.switchOverlay(this.overlay, false);
            this.refreshRouteProcessTable(result.data);
        }
    }

    renderError(error){
        if(this.method === 'GET'){
            console.info('加载CNC设计失败:', error);
            alert('加载现有CNC工序设计失败，请重试');}
        else{   
            console.info('保存失败:', error);
            alert('保存失败，请重试');
        }         
    }

    refreshRouteProcessTable(data) {
        // 找到对应的CNC工艺设计容器并刷新
        if (!data || !data.id || !data.text) return;
        const tabpan_id = this.modal.dataset.tabId;
        
        // 策略1：尝试通过 tabpan_id 查找
        let selecter = null;
        let tabpan = null;
        
        if (tabpan_id) {
            tabpan = document.querySelector(`#${tabpan_id} .tab-pane`);
            selecter = document.querySelector(`#${tabpan_id} select`);
            if (tabpan) {
                if (!selecter) {
                    selecter = tabpan.querySelector('select.el-select__inner');
                }
            }
        }
        if (selecter) {
            selecterRenderer.appendOptionV(selecter, data.id, data.text)
            selecter.value = data.id;
            selecter.dispatchEvent(new Event('change', { bubbles: true }));
            console.log(`成功更新选择器: ${data.id} - ${data.text}`);
        } else {
            console.warn(`未找到选择器元素: tabpan_id=${tabpan_id}, 尝试了多种查找策略`);
        }
    }

    loadExistingDesign(cncProcesses) {
        console.log('API response:', cncProcesses);

        if (!Array.isArray(cncProcesses) || cncProcesses.length === 0) {
            alert('该工艺线路没有CNC工序数据');
            return;
        }
        this.initialDesignModal();
        cncProcesses.forEach((cncProcess, index) => {
            this.loadAndRenderProcessCard(cncProcess)
        });
        CNCDesignModal.updateProcessNumbers();

    }

    loadAndRenderProcessCard(cncProcess) {
        const processCard = this.addProcessCard(cncProcess);

        const steps = cncProcess.steps || [];
        const stepsContainer = processCard.querySelector('.steps-container');

        if (steps.length > 0 && cncProcess.steps_step_ids && cncProcess.steps_parms) {
            const stepIds = Array.isArray(cncProcess.steps_step_ids) ? cncProcess.steps_step_ids : [];
            const stepName = Array.isArray(cncProcess.steps_step_ids) ? cncProcess.steps_step_names : [];
            const stepParms = Array.isArray(cncProcess.steps_parms) ? cncProcess.steps_parms : [];

            stepIds.forEach((stepId, stepIndex) => {
                const stepData = {
                    step_id: stepId,
                    step_name: stepName[stepIndex],
                    params: stepParms[stepIndex] || {}
                };
                this.addStep(processCard, stepData); // 使用空的 StepParams，因为数据已从 stepData 获取
            });
        } else {
            // 处理标准工步格式
            steps.forEach(step => {
                this.addStep(processCard, step);
            });
        }

        CNCDesignModal.updateStepNumbers(processCard);
    }
}

export class DesignModal extends CNCDesignModal {
    constructor(dataParams, StepParam = null, method = null, type = null) {
        super(dataParams, StepParam, method, type);
        const titleE = this.modal.querySelector('.cnc-modal-header-title');
        titleE.textContent = '工艺设计';
        const subtitleE = this.modal.querySelector('.cnc-card-header-title');
        subtitleE.textContent = '工序卡';
    }

    async handleFastFillDate(data) {
        if (!Array.isArray(data) || data.length === 0) {
            console.info('handleFastFillDate: 无效的数据格式或空数组');
            alert('没有找到需要添加的工序数据');
            return false;
        }

        try {
            // 清空现有的工序卡
            this.container.innerHTML = '';
            let processNo = 1;
            let rowErrors = [];

            // 处理每个工序数据
            for (const processItem of data) {
                if (!processItem.process_name || !processItem.type_name) {
                    console.warn('跳过无效的工序数据:', processItem);
                    continue;
                }

                // 1. 根据 type_name 更新 selecter_url.params
                const typeName = processItem.type_name;
                this.selecter_url.params = { type_name: typeName };
                
                // 2. 清除该type_name的缓存，确保加载新的工步列表
                CNCDesignModal.stepOptionsCache.delete(typeName);
                CNCDesignModal.stepOptionsPromise.delete(typeName);

                // 3. 将 process_name 以中文逗号 '，' 分割作为工步列表
                const processName = processItem.process_name.replace(/,/g, '，');
                const stepNames = processName.split('，').filter(name => name.trim() !== '');
                
                if (stepNames.length === 0) {
                    console.warn('工序名称没有有效的工步:', processItem.process_name);
                    continue;
                }

                // 4. 构建 validateAndConvertStepData() 所需的原始数据格式
                const rawStepData = stepNames.map(stepName => ({
                    step_name: stepName.trim(),
                    note: processItem.note || ''
                }));

                // 5. 使用父类的 validateAndConvertStepData() 验证和转换工步数据
                // 传入 typeName 参数，确保获取对应类型的工步列表
                let validatedSteps;
                try {
                    validatedSteps = await this.validateAndConvertStepData(rawStepData, typeName, processNo);
                } catch (error) {
                    rowErrors.push(`工序 ${processNo} "${processItem.process_name}" 工步验证失败:`);
                    // 如果验证失败，尝试使用原始工步名称继续
                    validatedSteps = rawStepData.map(step => ({
                        step_name: step.step_name,
                        step_id: 'temp_' + step.step_name,
                        params: { note: step.note }
                    }));
                }

                if (validatedSteps.length === 0) {
                    rowErrors.push('工序没有有效的工步数据:', processItem.process_name);
                    continue;
                }

                // 6. 创建工序数据并渲染工序卡
                const processData = this.createProcessFromSteps(validatedSteps, processItem);
                this.loadAndRenderProcessCard(processData);
                processNo = processNo + 1;
            }

            // 更新工序编号
            CNCDesignModal.updateProcessNumbers();

            if (this.container.children.length === 0) {
                alert('没有成功添加任何工序数据');
                return false;
            }
            if (rowErrors.length > 0) {
                alert(rowErrors.join('\n'));
            }

            return true;

        } catch (error) {
            console.info('handleFastFillDate error:', error);
            alert(error.message || '数据处理失败，请检查输入格式');
            return false;
        }
    }
}

export async function fetchDataAndRenderCNCDesignModal(dataParams=null, StepParam = null, method = null, type = null, tabPaneID = null) {
    const renderer = new CNCDesignModal(dataParams, StepParam, method, type);
    if (type) renderer.setType(type);
    if (tabPaneID) renderer.setActiveLab(tabPaneID);
    method = method? method : renderer.type === 'NEW'? 'POST' : 'PUT';
    const data = method !== 'GET' ? renderer.getData() : null;
    if (!data && method !== 'GET') return;
    fetchDataRenderFrame(renderer, method, data);
}

export function triggerCNCDesignModal(event, mode, StepParam) {
    const tabPane = event.target.closest('.tab-pane.active');
    const selector = tabPane.querySelector('select');
    const routeId = selector?.value;
    const table = tabPane.querySelector('table');
    let dataParams = JSON.parse(table.dataset.dataParams);
    if (!routeId && mode === 'Create') {
        const modelRender = dataParams.is_cnc? new CNCDesignModal(dataParams, StepParam) : new DesignModal(dataParams, StepParam)
        modelRender.initialDesignModal();
        modelRender.setType('NEW');
        modelRender.setActiveLab(tabPane.id)
        return;
    }else if (!routeId && mode === 'Edit') {
        alert('请先选择一个工艺线路');
        return;
    }
    dataParams.route = routeId;
    fetchDataAndRenderCNCDesignModal(dataParams, StepParam, 'GET', mode === 'Create' ? 'NEW' : 'EXISTING' , tabPane.id)
}
