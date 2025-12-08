import {floatingWindModelRender, dataCardRenderer, tableRenderer, selecterRenderer, BaseRenderer} from './renderFrame.js';
import { URLConfig, utils } from './utils.js';
import { H_ENDPOINTS, K_ENDPOINTS, API_CONFIG, K_HIDDENS } from './apiConfig.js';
import { fetchDataRenderFrame, renderFrameAndLoadData } from './eventAction.js';

const PARTINFO_KEYS = ['id','order_id','material_id','material_model','material_name','material_number','version', 'route', 'cnc_route']
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
    getResponeData(result){
        this.data = (result.data && (result.data.items || result.data)) || [];  // 默认空数组
        let data = []
        let p_items = {}
        if(this.table.classList.contains('route-process')){
            this.data.forEach(items => {
                p_items = {}
                items.steps_parms.forEach(item => {
                    const obj = JSON.parse(item);
                    Object.keys(obj).forEach(key => {
                        if (!p_items[key]) p_items[key] = [];
                        p_items[key].push(obj[key]);
                    });
                });
                items = { ...items, ...p_items }
                data.push(items)
            });
            this.data = data;
        }
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
        response = response.data || response;
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
    renderError(response) {
        alert(response.message || '数据上传失败!');
    }
}

class partDescriptions extends floatingWindModelRender
{
    constructor(container, dataParams=null) {
        super(container, null, null, null)
        this.dataParams = dataParams || {};
        const title = this.title;
        this.table_parmer =  {
            'headers': JSON.stringify(H_ENDPOINTS[APP][title]||[]),
            'keys': JSON.stringify(K_ENDPOINTS[APP][title]||[]),
            'hidkeys': JSON.stringify(K_HIDDENS[APP][title]||[]),
            'url': JSON.stringify({
                path:API_CONFIG[APP][title].path, params:URLConfig.buildApiParams(API_CONFIG[APP][title], this.dataParams)}),
            'dataParams': JSON.stringify(this.dataParams)} 
    }
    randerTableData()
    {
        renderFrameAndLoadData(this.tableDiv);
    }
}

export class partLabsDescriptions extends partDescriptions {
    constructor(container, dataParams = null , method = 'GET')
    {
        super(container, dataParams, null);
        this.url = {path:API_CONFIG[APP].lab_materials.path, 
            params:dataParams? URLConfig.buildApiParams(API_CONFIG[APP].lab_materials, dataParams) : {}};
            
        this.labTabContent = container.querySelector('.tab-content');
        this.labTabHeader = container.querySelector('.tab-header');
        this.labTab = container.querySelector('.custom-tabs');
        this.isCNC = this.title.includes('CNC');
        this.method = method;
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
    randerSelecter(data, value)
    {
        if(this.selecter){
            const selecterRender = new selecterRenderer(this.selecter)
            selecterRender.render(data); 
            if (value)
                selecterRender.updateSelected(value)
        }  
    }

    createLabTabItemPane(text, index)
    {
        const tabItem = document.createElement('div');
        tabItem.className = 'tab-item'; 
        tabItem.id = this.isCNC ? `CNC-${text}`: `${text}`;
        tabItem.textContent = tabItem.id;
        if(index === 0) tabItem.classList.add('active'); 
        if(this.isCNC) tabItem.classList.add('CNC'); 
        this.labTabHeader.appendChild(tabItem);
        const tabPane = document.createElement('div');
        tabPane.className = 'tab-pane';
        tabPane.id = this.isCNC ? `CNC-${text}`: `${text}`;
        if(index === 0) tabPane.classList.add('active'); 
        if(this.isCNC) tabPane.classList.add('CNC'); 
        this.labTabContent.appendChild(tabPane);
        return tabPane
    }
    render(result)
    {
        if (this.method == 'POST'){
            alert(result.message || '数据上传成功!'); 
            return}
        BaseRenderer.clearContainer(this.labTabHeader);        
        BaseRenderer.clearContainer(this.labTabContent);
        if(!result || !result.data || !Array.isArray(result.data) || result.data.length === 0) return;  

        result.data.forEach((dataItem, index) => {
            const dataParams = utils.updateDict(this.dataParams, dataItem);
            dataParams.isCNC = this.isCNC;           
            this.table_id = dataParams.material_model;
            this.select_params =  {
                option :JSON.stringify({defaultText: '请选择历史工艺线路设计', key: 'id', textK: 'text'})}
            this.button_group = 
                [{id:'compile-existing', text:'编译已有工序设计', className:'el-button el-button--primary el-button--small'},
                 {id:'new-route', text:'开始新工序设计', className:'el-button el-button--warning el-button--small'}]
              //  [{id:'row-remove', text:'撤销工序', className:'el-button el-button--warning el-button--small'},
              //      {id:'new-process', text:'添加工序', className:'el-button el-button--primary el-button--small'},
              //      {id:'table-save', text:'保存', className:'el-button el-button--primary el-button--small'}]
            this.table_parmer =  {
                'headers': JSON.stringify(H_ENDPOINTS[APP][this.title]||[]),
                'keys': JSON.stringify(K_ENDPOINTS[APP][this.title]||[]),
                'hidkeys': JSON.stringify(K_HIDDENS[APP][this.title]||[]),
                'url': JSON.stringify({ path:API_CONFIG[APP][this.title].path, params:URLConfig.buildApiParams(API_CONFIG[APP][this.title], dataParams)}),
                'dataParams': JSON.stringify(dataParams),
                'buttons': JSON.stringify(['编辑'])} 
            const tabPane = this.createLabTabItemPane(dataParams.material_model, index);
            const select_data = this.isCNC ? dataItem.cnc_route_list : dataItem.route_list;
            const route_id = this.isCNC ? dataItem.cnc_route : dataItem.route;
            
            this.createExtra(tabPane);
            this.createBody(tabPane);
            this.createFooter(tabPane);
            this.randerSelecter(select_data, route_id);
            this.selecter.id = tabPane.id
            partLabsDescriptions.randerTableDataViSelecter(tabPane);
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
    renderError (response) {
        alert(response.message || '数据上传失败!');
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
    static toggleEditButtons(container, button) {
        const isActive = button.classList.contains('btn-active');
        if(!container) return;

        if (isActive) button.classList.remove('btn-active');
        else button.classList.toggle('btn-active', true);

        const editButtons = container.querySelectorAll('button[data-edit]');
        editButtons.forEach(button => {
            button.style.display = !isActive ? 'flex' : 'none';  //'inline-block'
        })
    } 
    static hideContainSwitch(container, button) {
        if (!button || !button.parentNode) return;
        button = button.nodeName === 'BUTTON' ? button : button.parentNode;
        const icon = button.querySelector('#collapseIcon');
        const btnText = button.querySelector('span');
        const parts_tabs = container.querySelector('.custom-tabs');

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
        }
    }

    static randerTableDataViSelecter(panel){
        const selectHelp = panel.querySelector('#select-help-note');
        const table = panel.querySelector('table');
        const selecter = panel.querySelector('select');

        const routeId = selecter.value;
        const text = selecter.options[selecter.selectedIndex].textContent.trim();
        if (!routeId) return;

        const dataParams = JSON.parse(table.dataset.dataParams);
        if (selectHelp && dataParams.order_id)
            selectHelp.textContent = `订单: ${dataParams.order_id||''} 确认加工 ${text}`
        
        table.dataset.url = JSON.stringify({path: API_CONFIG[APP]['工艺线路'].path, endpoint: routeId});
        renderFrameAndLoadData(table)        
        table.classList.add('route-process');
    }

    static panelSwitch(container, tabItem) {
        const target = container.querySelector('.tab-item.active');
        target.classList.remove('active');
        tabItem.classList.add('active');
        const tabPane = container.querySelector('.tab-pane.active');
        tabPane.classList.remove('active');
        const tabContentId = tabItem.id;    
        const tabContentEl = document.querySelector(`#${tabContentId}.tab-pane`);
        tabContentEl.classList.add('active');   
    }
}

export function renderPartDetailModalFrame(dataParams, modal, text_title){
    const titleTextDiv = modal.querySelector('.title-text');
    titleTextDiv.textContent = text_title;
    modal.dataset.dataParams = JSON.stringify(dataParams);

    const childrens = modal.querySelectorAll(`[id^="parts-descriptions-"]`)
    childrens.forEach(async children =>{
        const is_lab_panel = children.classList.contains('lab-panel');
        if (!is_lab_panel) {    
            const partDesc = new partDescriptions(children, dataParams);    
            partDesc.initialize();
        }else{
            const partDescLeb = new partLabsDescriptions(children, dataParams);
            partDescLeb.initialize();
            fetchDataRenderFrame(partDescLeb);
        }
    })
}
