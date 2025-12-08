import {handleToggleButton, fastFillModelRenderer, tableRenderer, dataCardRenderer, selecterRenderer } from "./renderFrame.js";
import {utils, URLConfig, ModalStackManager} from './utils.js';
import {H_ENDPOINTS, K_ENDPOINTS, T_ENDPOINTS, K_HIDDENS, API_CONFIG} from './apiConfig.js';
import { renderFrameAndLoadData, TablerHandler, fetchDataRenderFrame, } from './eventAction.js';
import {renderPartDetailModalFrame, partLabsDescriptions} from './t_modalPartsDetail.js';
import {DesignModal, CNCDesignModal, triggerCNCDesignModal, NUMERIC_UNITS, fetchDataAndRenderCNCDesignModal} from './t_modalCncDesign.js';

const PARTINFO_KEYS = ['id','order_id','material_id','material_model','material_name','material_number','version', 'route', 'cnc_route']
const FILTER_KEYS = ["material_number","material_model","status"];
const APP = 'c_gongyi';


// 快速添加CNC工序功能
export function renderFastAddCNCProcess(Params, isCNC = true) {
    Params = isCNC? Params['CNC'] : Params['UNCNC']
    const fastContain = document.querySelector('.el-descriptions-fast-fill')
    const headers = isCNC? ['工步名称', ...Params.map(h => h.label)] : ['工序名称','设备', ...Params.map(h => h.label)];
    const keys = isCNC? ['step_name', ...Params.map(h => h.key)] : ['process_name','type_name', ...Params.map(h => h.key)];
    const numbers = keys.filter(item => NUMERIC_UNITS.some(keyword => item.includes(keyword)))

    const table_params = {
        headers: JSON.stringify(headers),
        keys: JSON.stringify(keys),
        require: JSON.stringify(['step_name']),
        numbers: JSON.stringify(numbers)
    }
    const renderer = new fastFillModelRenderer(fastContain, null, table_params);    
    renderer.initialize();
}

function bindInputsForFilter(container, table) {
    let detail = [];
    let params = {};
    const orderId = container.dataset.filterOrderId;
    table.dataset.groupkey = 'order_id';
    if (orderId) {
        detail.push(`订单号: ${orderId}`);
        params['order_id'] = orderId;
        table.dataset.groupkey = '';}
    FILTER_KEYS.forEach(key => {
        const val = container.querySelector(`#${key}`).value.trim();
        if (val) {
            detail.push(`${key}: ${val}`);
            params[key] = val;}
    })
    document.getElementById('filter-detail-content').textContent = detail.length ? detail.join('，') : '无';
    return params
}

export function handlePartsTableSelectEvent(container, modal) {
    container.addEventListener('click', e => {
        if (!e.target.matches('td')) return;
        const tr = e.target.closest('tr');
        if (tr && tr.classList.contains('parent-row') && tr.classList.contains('expanded')) return;
        const order_part = new TablerHandler(e.target.closest('table')).getTrData(tr, PARTINFO_KEYS);
        if (!order_part.data) return;
        const dataParams = order_part.data;
        utils.switchOverlay(modal, true);
        renderPartDetailModalFrame(dataParams, modal, `${dataParams.material_name}  ${dataParams.material_model}`);
    });
}

export function handleOrderPartFilterEvent(container, loadtable) {
    container.addEventListener('click', e => {
        if (e.target.matches('td')) {
            const order = new TablerHandler(e.target.closest('table')).getTrData(e.target.closest('tr'),  ['order_id']);
            container.dataset.filterOrderId = order.data.order_id;
            const url_parm = bindInputsForFilter(container, loadtable);
            loadtable.dataset.url = JSON.stringify({path: API_CONFIG['b_jihua'].get_order_parts, params: url_parm});
            renderFrameAndLoadData(loadtable);
        };
        if (e.target.matches('#filter-confirm-btn')){
            const url_parm = bindInputsForFilter(container, loadtable);
            loadtable.dataset.url = JSON.stringify({path: API_CONFIG['b_jihua'].get_order_parts, params: url_parm});
            renderFrameAndLoadData(loadtable);
        }
    })
    loadtable.addEventListener('change', e => {
        if (e.target.matches('select')) {
            const tbHander = new TablerHandler(loadtable, 'PUT', false);
            tbHander.update(e.target.closest("tr"))
        };
    })

}

export function handlePartDetailModalEvent(modal, STEPARAM = null) {
    modal.addEventListener('click', e => {
        if (e.target.matches('#switch-modal'))
            utils.switchOverlay(modal, false);
        if (e.target.matches('#maximize-modal'))
            utils.maximizeModal(modal, 'main');
        if (e.target.matches('#modal_edit'))
            partLabsDescriptions.toggleEditButtons(modal, e.target);
        //if (e.target.matches('#row-remove'))
        //    new TablerHandler(e.target.closest(".tab-pane").querySelector('.el-descriptions__body table')).deleteRow();
        //if (e.target.matches('#new-process')){
        //    new ProcessEditer(document.querySelector('#process-design-modal')).modelActive(
        //        e.target.closest(".tab-pane").querySelector('.el-descriptions__body table'));}
        //if (e.target.matches('#process_edit')){
        //    new ProcessEditer(document.querySelector('#process-design-modal')).modelActive(
        //        e.target.closest(".tab-pane").querySelector('.el-descriptions__body table'), e.target.closest("tr"));}
        //if (e.target.matches('#table-save'))
        //    new TablerHandler(e.target.closest(".tab-pane").querySelector('.el-descriptions__body table'), 'POST').update();
        if (e.target.matches('#selecter-save')){
            const tabs = e.target.closest('.tab-content').querySelectorAll('.tab-pane');
            let warning = []
            let parts = []
            tabs.forEach( tab => {
                const selecter = tab.querySelector('select');
                if (selecter.value === '') 
                    warning.push(`${tab.id} 请选择合适的工艺路线 `) 
                else {
                    const table = tab.querySelector('table');
                    let data = JSON.parse(table.dataset.dataParams);
                    data.route = selecter.value;
                    parts.push(data)
                }
            })
            if (warning.length > 0) {
                alert(warning.join('\n'));}
            else {
                updateProductionRoute(parts, e.target.closest('.el-descriptions'));
            }
        }
        if (e.target.matches('.collapse-btn') || e.target.parentNode.matches('.collapse-btn')){
            const container = e.target.closest('.el-descriptions');
            partLabsDescriptions.hideContainSwitch(container, e.target);
        }
        if(e.target.matches('.tab-item'))
            partLabsDescriptions.panelSwitch(e.target.closest('.custom-tabs'),e.target)
        if (e.target.matches('#new-route')) {
            e.preventDefault();
            triggerCNCDesignModal(e, 'Create', STEPARAM)
        }
        if (e.target.matches('#compile-existing')) {
            e.preventDefault();
            triggerCNCDesignModal(e, 'Edit', STEPARAM)
        }
    },300);

    modal.addEventListener('change', e => {
        if (e.target.matches('select')) {
            const partDesc = e.target.closest(".tab-pane");
            partLabsDescriptions.randerTableDataViSelecter(partDesc);
        }
    });
}

export function handleCNCDesignModalEvent(modal, STEPARAM)
{
    modal.addEventListener('click', e => {

        if (e.target.matches('.toggle-steps') || e.target.closest('.toggle-steps')) {
            const button = e.target.closest('.toggle-steps');
            const processCard = button.closest('.cnc-process-card');
            const stepsContainer = processCard.querySelector('.steps-container');
            handleToggleButton(stepsContainer, button);
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
        if (e.target.matches('.add-step')){
            const modelRenderer = new CNCDesignModal(null, STEPARAM)
            if (modelRenderer.validateFormInputs(e.target.closest('.cnc-process-card')))
                modelRenderer.addStep(e.target.closest('.cnc-process-card')) 
            }
        if (e.target.matches('#save-cnc-design'))
            if (new CNCDesignModal().validateFormInputs(e.target.closest('.cnc-processes-container')))
                fetchDataAndRenderCNCDesignModal(null, STEPARAM)
        if (e.target.matches('#add-cnc-process'))
            new CNCDesignModal(null, STEPARAM).addProcessCard()
        if (e.target.matches('#fast-add-cnc-process')){
            const dataParams = JSON.parse(modal.dataset.dataParams || '{}');
            renderFastAddCNCProcess(STEPARAM.Params, dataParams.isCNC)
            utils.switchOverlay(document.querySelector('#quick-fill-modal'), true);
        }
        if (e.target.matches('#switch-modal'))
            utils.switchOverlay(modal, false);
        if (e.target.matches('#maximize-modal'))
            utils.maximizeModal(modal, '.el-dialog__body');
        if (e.target.matches('#cancel-cnc-design')) utils.switchOverlay(modal, false)
    })
    modal.addEventListener('change', e => {
        if (e.target.matches('.device-select')) {
            const dataParams = JSON.parse(modal.dataset.dataParams || '{}');
            if (!dataParams.isCNC) {
                const container = e.target.closest(".cnc-process-body").querySelector(".steps-container");
                if (container) {
                    while (container.firstChild) container.firstChild.remove();
                }
            }
        }
    });
}

export async function handleFastAddCNCProcess(event, params) {
    const container = event.target.closest('#quick-fill-modal');
    const table = container.querySelector('table');
    const handler = new TablerHandler(table)
    if (handler.getData() !== 'ok') {
        console.error('表格数据检查失败');
        return;
    }

    const cncModalElement = document.getElementById('cnc-design-modal');
    if (!cncModalElement) {
        console.error('CNC设计模态框不存在');
        return;
    }

    let dataParams = {};
    try {
        dataParams = JSON.parse(cncModalElement.dataset.dataParams || '{}');
    } catch (e) {
        console.warn('解析模态框数据参数失败:', e);
    }

    const cncModal = dataParams.isCNC ? new CNCDesignModal(dataParams, params) : new DesignModal(dataParams, params);
    const result = await cncModal.handleFastFillDate(handler.data);
    if (result) {
        setTimeout(() => {
            utils.switchOverlay(container, false);
        }, 500);
    }
}

async function updateProductionRoute(parts, el_descriptions) {
    if (!parts || !Array.isArray(parts) || parts.length === 0) {
        alert('没有需要更新的零件数据');
        return;
    }
    let data = []
    for (const part of parts) {
        data.push({
            order_part: part.material_id,
            route: part.isCNC ? null : part.route,
            cnc_route: part.isCNC ? part.route : null,
            status: 'planned',
            order_id: part.order_id,
            description: `工艺路线已确认 - ${part.material_name || part.material_model}`
        })
    }
    const renderer = new partLabsDescriptions(el_descriptions, null, 'POST');
    await fetchDataRenderFrame(renderer, 'POST', data);
}
