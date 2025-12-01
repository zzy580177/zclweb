import {BaseRenderer, floatingWindModelRender, tableRenderer, dataCardRenderer, selecterRenderer } from "./renderFrame.js";   
import {utils, URLConfig} from './utils.js';
import {H_ENDPOINTS, K_ENDPOINTS, T_ENDPOINTS, K_HIDDENS, API_CONFIG} from './apiConfig.js';
import {fetchDataRenderFrame, renderTableAndLoadData, TablerHandler} from './eventAction.js';

const PARTINFO_KEYS = ['id','order_id','material_id','material_model','material_name','material_number','version']
const FILTER_KEYS = ["material_number","material_model","status"];
const APP = 'c_gongyi';

export class descriptionsTable extends tableRenderer {
    constructor(table, params = null) {
        super(table, params); 
        if(this.table){       
            this.table.className = 'el-descriptions__table';
            this.table.style.width = '100%';
            this.table.style.borderCollapse = 'collapse';
            //this.id = this.table.id;
        }
        
        this.isEditActive = document.querySelector('#modal_edit')?.classList?.contains('btn-active') || false;
        this.display = this.isEditActive ? 'flex' : 'none';
    }
    postRender(response){
        if(!response) return
        alert(response.message || '数据上传成功!');
        if(response.routeId){
            if(response.routeId != this.table.dataset.endpoint)
            {
                this.table.dataset.endpoint = response.routeId
                const selecter = this.table.parentNode.previousElementSibling.querySelector('select')
                selecterRenderer.appendOptionV(selecter, response.routeId, response.text)
                selecter.value = response.routeId;
                selecter.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }
    }
    postRenderError(response) {
        const errorMessage = [response?.message, 
            Array.isArray(response?.Error) ? response.Error.join('\n') : ''
        ].filter(Boolean).join('\n\n') || '发生未知错误';
        alert(errorMessage);
    }
    createButtonForCell(key)
    {
        const button = document.createElement('button');
        button.textContent = key;
        button.id = 'process_edit';
        button.className = 'el-button el-button--warning el-button--small';
        button.dataset.edit = this.isEditActive;
        button.style.display = this.display;
        return button
    }
}

export class partDescriptions extends floatingWindModelRender
{
    constructor(container, data_params=null, button_group=null) {
        super(container, null, null, button_group)
        this.data_params = data_params || {};
        const title = this.title;
        this.table_id = `${T_ENDPOINTS[title]||''}-${this.data_params['material_model']||''}`;
        this.table_parmer =  {
            'headers': JSON.stringify(H_ENDPOINTS[APP][title]||[]),
            'keys': JSON.stringify(K_ENDPOINTS[APP][title]||[]),
            'hidkeys': JSON.stringify(K_HIDDENS[APP][title]||[]),
            'url': JSON.stringify(API_CONFIG[APP][title].path),
            'url_params': JSON.stringify(URLConfig.buildApiParams(API_CONFIG[APP][title], this.data_params)),
            'data_params': JSON.stringify(this.data_params)
        } 
    }
    randerTableData()
    {
        const tableRender = this.container.dataset.body === 'table'? 
            new descriptionsTable(this.tableDiv) : new dataCardRenderer(this.tableDiv);        
        fetchDataRenderFrame(tableRender);
    }
}

export class partLabsDescriptions extends partDescriptions {
    constructor(container, data_params = null)
    {
        super(container, data_params, null);
        this.url = API_CONFIG[APP].lab_materials.path
        this.url_params = data_params? URLConfig.buildApiParams(API_CONFIG[APP].lab_materials, data_params) : {};
        this.labTabContent = container.querySelector('.tab-content');
        this.labTabHeader = container.querySelector('.tab-header');
        this.labTab = container.querySelector('.custom-tabs');
        this.isCNC = this.title.includes('CNC');
    }

    initialize(){
        this.container.innerHTML = '';
        this.createHeader()
        this.createLine('#0d47a1');
        this.initial_labTab();
    }

    initial_labTab(container = this.container)
    {
        this.labTab = document.createElement('div');
        this.labTab.className = 'custom-tabs';
        this.labTabHeader = document.createElement('div');
        this.labTabHeader.className = 'tab-header';
        this.labTab.appendChild(this.labTabHeader);
        this.labTabContent = document.createElement('div');
        this.labTabContent.className = 'tab-content';
        this.labTab.appendChild(this.labTabContent);        
        container.appendChild(this.labTab);
    }

    createLabTabItemPane(text, index)
    {
        const tabItem = document.createElement('div');
        tabItem.className = 'tab-item'; 
        tabItem.id = this.isCNC ? `${text}-CNC`: `${text}`;
        tabItem.textContent = text;
        if(index === 0) tabItem.classList.add('active'); 
        if(this.isCNC) tabItem.classList.add('CNC'); 
        this.labTabHeader.appendChild(tabItem);
        const tabPane = document.createElement('div');
        tabPane.className = 'tab-pane';
        tabPane.id = this.isCNC ? `${text}-CNC`: `${text}`;
        if(index === 0) tabPane.classList.add('active'); 
        if(this.isCNC) tabPane.classList.add('CNC'); 
        this.labTabContent.appendChild(tabPane);
        return tabPane
    }
    render(result)
    {
        BaseRenderer.clearContainer(this.labTabHeader);        
        BaseRenderer.clearContainer(this.labTabContent);
        if(!result || !Array.isArray(result) || result.length === 0) return;  

        result.forEach((dataItem, index) => {
            dataItem.order_id = this.data_params.order_id;   
            dataItem.isCNC = this.isCNC;           
            this.table_id = `${T_ENDPOINTS[this.title]||''}-${dataItem.material_model||''}`;
            this.select_params =  {
                defaultText: '请选择历史工艺线路设计', key: 'id', textK: 'text',
                url: JSON.stringify(API_CONFIG[APP].route_selecter), 
                url_params: JSON.stringify({material_id: dataItem.material_id, isCNC:this.isCNC})
            }
            this.button_group = this.isCNC ?
                [{id:'compile-existing', text:'编译已有CNC工序设计的', className:'el-button el-button--primary el-button--small'},
                 {id:'new-route', text:'开始CNC工序设计', className:'el-button el-button--warning el-button--small'}]:
                [{id:'row-remove', text:'撤销工序', className:'el-button el-button--warning el-button--small'},
                    {id:'new-process', text:'添加工序', className:'el-button el-button--primary el-button--small'},
                    {id:'table-save', text:'保存', className:'el-button el-button--primary el-button--small'}]
            this.table_parmer =  {
                'headers': JSON.stringify(H_ENDPOINTS[APP][this.title]||[]),
                'keys': JSON.stringify(K_ENDPOINTS[APP][this.title]||[]),
                'hidkeys': JSON.stringify(K_HIDDENS[APP][this.title]||[]),
                'url': JSON.stringify(API_CONFIG[APP][this.title].path),
                'url_params': JSON.stringify(URLConfig.buildApiParams(API_CONFIG[APP][this.title], dataItem)),
                'data_params': JSON.stringify(dataItem),
                'buttons': JSON.stringify(['编辑'])} 
            const tabPane = this.createLabTabItemPane(dataItem.material_model, index);
            this.createExtra(tabPane);
            this.createBody(tabPane);
            this.createFooter(tabPane);
            this.randerSelecter();
            this.randerTableData();
        });
        this.container.switchTab = (index) => {
            const panes = this.container.querySelectorAll('.tab-pane');
            const items = this.container.querySelectorAll('.tab-item');
            panes.forEach(pane => pane.classList.remove('active'));
            items.forEach(item => item.classList.remove('active'));
            panes[index].classList.add('active');
            items[index].classList.add('active');
        };
    }
    renderButtonGroup()  // fmdoel is not used, but kept for compatibility
    {
        const isEditActive = document.querySelector('#modal_edit').classList.contains('btn-active');
        const display = isEditActive ? 'inline-flex' : 'none';
        this.footerDiv.innerHTML = ''; // 清空现有内容
        const buttonContainer = document.createElement('div');
        buttonContainer.style.marginTop = '10px';
        buttonContainer.style.textAlign = 'right';
        buttonContainer.style.display = 'flex';

        this.button_group.forEach(btnInfo => {
            const button = document.createElement('button');
            button.id = btnInfo.id || '';
            button.className = btnInfo.className || 'el-button el-button--primary el-button--small';
            button.textContent = btnInfo.text || '按钮';
            button.dataset.edit = isEditActive;
            button.style.display = display;
            buttonContainer.appendChild(button);
        });
        this.footerDiv.appendChild(buttonContainer);

        const select_button = document.createElement('button');            
        select_button.id = 'selecter-save'
        select_button.className = 'el-button el-button--primary    el-button--small';
        select_button.textContent = '确认';
        select_button.dataset.edit = isEditActive;
        select_button.style.display = display;
        select_button.style.float = 'right';

        this.extraDiv.appendChild(select_button);
    }
    static toggleEditButtons(container, isVisible) {
        if(!container) return;
        const editButtons = container.querySelectorAll('button[data-edit]');
        editButtons.forEach(button => {
            button.style.display = isVisible ? 'flex' : 'none';  //'inline-block'
        })
    }
}

function renderPartDetailModalFrame(order_part, modal){
    const titleTextDiv = modal.querySelector('#parts-detail-modal-title');
    titleTextDiv.textContent = `${order_part['material_model']}  ${order_part['material_name']}`;
    titleTextDiv.setAttribute('title', `${order_part['material_model']}  ${order_part['material_name']}`);
    modal.dataset.orderPart = JSON.stringify(order_part);

    const childrens = modal.querySelectorAll(`[id^="parts-descriptions-"]`)
    childrens.forEach(async children =>{
        const title = children.getAttribute('data-title');
        if (!['工艺线路','CNC工艺设计'].some(keyword => title.includes(keyword))) {    
            const partDesc = new partDescriptions(children, order_part);    
            partDesc.initialize();
        }else{
            const partDescLeb = new partLabsDescriptions(children, order_part);
            partDescLeb.initialize();
            fetchDataRenderFrame(partDescLeb);
        }
    })
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
        const order_part = utils.getSelectedCellValue(e.target, PARTINFO_KEYS);
        if (!order_part) return;
        utils.switchOverlay(modal, true);
        renderPartDetailModalFrame(order_part, modal);
    });
}

export function handleOrderPartFilterEvent(container, loadtable) {
    container.addEventListener('click', e => {
        if (e.target.matches('td')) {
            const orderId = utils.getSelectedCellValue(e.target, ['order_id'])
            container.dataset.filterOrderId = orderId['order_id'];
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
    loadtable.addEventListener('change', e => {
        if (e.target.matches('select')) {
            const tbHander = new TablerHandler(loadtable, 'PUT', false);
            tbHander.update(e.target.closest("tr"))
        };
    })

}
