import { descriptionsTable } from './t_modalPartsDetail.js';
import {tableRenderer, postTableRenderer, selecterRenderer, dataCardRenderer } from './renderFrame.js';
import {loadingOverlay, utils} from './utils.js'


const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

function getUrl(frameRenderer, method)
{
    const url_info = frameRenderer?.url || {}
    const url = url_info.path? url_info.path[method] || '' : url_info[method] ||''
    const endpoint = method === 'POST' ? '' : frameRenderer.endpoint !== undefined? frameRenderer.endpoint:url_info.endpoint || '';
    const params = frameRenderer.url_params !== undefined? frameRenderer.url_params:url_info.params || {};
    
    return {url:url, endpoint:endpoint, params:params}
}

export class ApiHandler {
    constructor(baseURL) {
        this.baseURL = baseURL.endsWith('/') ? baseURL.slice(0, -1) : baseURL;
        this.pendingRequests = new Set();
    }

    async request({
        method = 'GET',
        endpoint = '',
        params = {},
        data = null,
        renderSelector = null,
        onSuccess = null,
        onError = null,
        toggleLoad = null
    }) {
        const queryString = this.buildQueryString(params);
        const url = endpoint? `${this.baseURL}/${endpoint.replace(/^\//, '')}`: 
            `${this.baseURL}${queryString}`;
        const requestId = `${method}_${url}`;

        try {
            this.toggleLoading(toggleLoad, true);
            this.pendingRequests.add(requestId);

            const response = await fetch(url, { method,
                credentials: 'same-origin',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                ...(data && { body: JSON.stringify(data) })
            });

            let result = await this.parseResponse(response);
            result = await this.parseResponseData(result)
            
            if (renderSelector && document.querySelector(renderSelector)) {
                this.renderResult(renderSelector, result);
            }
            if (!result.success) {
                onError?.(result)
            }else{
                
                onSuccess?.(result);
                return result;
            }
        } catch (error) {
            this.showDefaultError(error);
            throw error;
        } finally {
            this.pendingRequests.delete(requestId);
            this.toggleLoading(toggleLoad, false);
        }
    }

    buildQueryString(params) {
        const entries = Object.entries(params).filter(([_, value]) => value !== undefined && value !== null)
            .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`);
        return entries.length ? `?${entries.join('&')}` : '';
    }

    renderResult(selector, data) {
        const container = document.querySelector(selector);
        if (!container) return;        
        container.innerHTML = typeof data === 'object' 
            ? JSON.stringify(data, null, 2) 
            : String(data);
    }

    toggleLoading(element, state) {
        if (!element) return;        
        if (state)
            loadingOverlay.show()
        else
            loadingOverlay.hide()
    }

    parseResponse(response) {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }

    parseResponseData(data)
    {
        const success = data?.data?.success ?? data?.success ?? true;
        const mainData = data?.data?.data ?? data?.data ?? data;                    
        return {
            success: success, 
            data: mainData, 
            message: data?.data?.message ?? data?.message};
    }

    showDefaultError(error) {
        console.error('API Error:', error);
        alert(`操作失败: ${error.message}`);
    }
}

export async function fetchDataRenderFrame(frameRenderer, method = 'GET', data = null,
     onSuccess = null, onError = null) {  
    const {url, endpoint, params} = getUrl(frameRenderer, method);
    if(url === '' || url === null || (url.endsWith('/') && !endpoint)) {
        console.info('url 为空');
        frameRenderer?.url?.datas?  frameRenderer.render(frameRenderer.url.datas):  frameRenderer.render()
        return;
    }
   
    const api = new ApiHandler(url);
    try {
        await api.request({
            method: method,
            data: data,
            endpoint: endpoint,
            params: params,
            toggleLoad: frameRenderer.toggleLoad,
            onSuccess: (response) => {
                if (onSuccess) {
                    onSuccess(response);
                } else {
                    frameRenderer.render(response);
                }
            },
            onError: (error) => {
                if (onError) {
                    onError(error);
                } else {
                    frameRenderer.renderError(error);
                }
            }
        });
    } catch (error) {
        console.error('fetchDataRenderFrame: Unexpected error:', error);
        alert('API获取失败，请稍后重试');
    }
}

export async function fetchDataForTableRow(renderer, rowIdx) {      
    const {url, endpoint, params} = getUrl(frameRenderer, 'GET');
    if(url === '' || url === null || (url.endsWith('/') && !endpoint)) {
        console.info('url 为空');
        frameRenderer?.url?.datas?  frameRenderer.render(frameRenderer.url.datas):  frameRenderer.render()
        return;
    }
    const api = new ApiHandler(url);
    try {
        await api.request({
            method : 'GET',
            endpoint : endpoint,
            params: params,
            toggleLoad: renderer.toggleLoad,
            onSuccess: (response) => {
               renderer.renderRow(response.data, rowIdx);
            },
            onError: (error) => {
               renderer.doNonThing(error);
            }});
    } catch (error) {
        console.error('Unexpected error:', error);
        alert('API获取失败，请稍后重试');
    }
}

export class TablerHandler {
    constructor(table, method = 'GET', isResultList=false) {
        this.table = table;
        this.url = JSON.parse(table.dataset.url || '{}');
        this.data = null;
        this.dataParams = JSON.parse(table.dataset.dataParams || '{}')
        this.method = method;
        this.result = 'ok';
        this.toggleLoad = true;
        this.isResultList = isResultList;
        this.target = table.querySelector('tbody');
    }
    validateFormInputs(target) {
        const requiredFields = target.querySelectorAll('input[required], select[required]');
        requiredFields.forEach(element => {element.classList.remove('unvalid');});
        const invalidEl = [];
        requiredFields.forEach(element => { if (!element.checkValidity()) {
            element.classList.add('unvalid');
            invalidEl.push(element);
        }});
        return invalidEl.length === 0;
    }
    async getDataByUniqKey(input){
        const uniqKeys = JSON.parse(this.table.dataset.uniqKeys || '[]');
        this.target = input.closest('tr')
        const data = this.getTrData(this.target); 
        let hasUniqK = false 
        let url_params = {}      
        for (const key of uniqKeys) {
            if (data?.data?.[key]) {
                url_params = { [key]: data?.data?.[key] };
                hasUniqK = true
                break;}
        }
        if (hasUniqK){
            const tableRender = new tableRenderer(this.table)
            tableRender.url_params = url_params;
            await fetchDataForTableRow(tableRender, this.target.rowIndex); }         
    }

    async submitDataAndPost()
    {
        if(!this.validateFormInputs(this.table)) return;
        await renderFrameAndLoadData(this.table, this.method,  null, this.toggleLoad);
    }

    async update(target = this.target) {
        if (!this.table) return console.error('Table not found') || false;
        this.result = this.getData(target);
        if(target.nodeName == 'TR') 
            this.table.dataset.endpoint = this.endpoint;
        return this.result === 'ok' 
            ? await renderFrameAndLoadData(this.table, this.method,  this.data, this.toggleLoad) || true
            : this.result;
    }

    getData(target = this.target){        
        if(!this.validateFormInputs(target))             
            return 'checkValidityFailed';
        if(target.nodeName == 'TR'){
            const result = this.getTrData(target);
            this.data = result.data;
            this.endpoint = result.endpoint;
        }else{
            this.data = []
            const rows =  target.querySelectorAll('tr');
            rows.forEach( row => this.data.push(this.getTrData(row).data))
        }
        if(this.data.length == 0) return 'checkDataEmpty';
        return 'ok'
    }
    getTrData(row, selecteds = []){
        if(!row) return { data: {}, endpoint: '' };
        if(this.isResultList) return this.getTrData_ResultList(row)
        const rawData = Object.assign({}, this.dataParams)
        const tds = row.getElementsByTagName('td');
        Array.from(tds).forEach(td => {
            if(td.querySelector('button')) return
            const divs = td.querySelectorAll('div');
            const key = td.dataset.key;  
            if( selecteds.length > 0 && !selecteds.includes(key)) return;            
            if(td.querySelector('select')){
                const select = td.querySelector('select')
                rawData[key] = select.value
            }
            else{  
                if(divs.length > 0) {
                    rawData[key] = Array.from(divs).map(div => div.textContent.trim());
                } else {
                    rawData[key] = td.firstChild ? 
                        (td.firstChild.value || td.firstChild.textContent.trim()) : 
                        td.textContent.trim();
                }
                rawData[key] = rawData[key] === '请选择'? '' : rawData[key];
            }
        });
        return { data: rawData, endpoint: rawData.Id || rawData.id || '' };
    }

    getTrData_ResultList(row){
        const rawData = {}
        let endpoint = '';
        const th= row.getElementsByTagName('th')[0];
        if(th){
            endpoint = th.firstChild?.value|| th.firstChild?.textContent.trim()|| th.textContent.trim()
        }
        // 处理td元素
        const tds = row.getElementsByTagName('td');
        Array.from(tds).forEach(td => {
            let className = td.className;
            if (className.includes('field') & !className.includes('action')) {
                let key = className.split(' ')[0].replace(/^field-|_option$/g, '');
                let val = td.firstChild?.value|| td.firstChild?.textContent.trim()|| td.textContent.trim()
                rawData[key] = val.replace(/-/g, '');
            }
        });
        return { data: rawData, endpoint: endpoint };
    }

    async pageLoad(target){
        if(!this.table) {
            console.error('Table not found');
            return false;
        }
        this.table.dataset.page = target.dataset.page||1
        await renderFrameAndLoadData(this.table);
    }
    addRow(){
        const tableBody = this.table.querySelector('tbody');
        const firstRow = tableBody.querySelector("tr");
        if (!firstRow) {
            console.error("addRow: 表格体中没有找到任何行");
            return;
        }
        const newRow = firstRow.cloneNode(true);
        const inputs = newRow.querySelectorAll("input, select");
        inputs.forEach(input => {
            if (input.tagName === "INPUT") input.value = "";
            else if (input.tagName === "SELECT") input.selectedIndex = 0;
        });
        tableBody.appendChild(newRow);
        return newRow;
    }
    deleteRow(target){
        const tableBody = this.table.querySelector('tbody');
        const minLen = target?1:0
        if (tableBody?.children?.length >minLen) {
            if(target) target.remove();
            else {
                const row = tableBody.rows[tableBody.rows.length - 1];
                row.remove();
            }
        } else {
            alert("至少保留一行！");
        }
    }
    static getSelectCellData(row, key){

    }
}

export async function renderFrameAndLoadData(container, method='GET', data=null, isToggleLoad = true) {
    const clist = container.classList;
    let tableRender = null;
    if (container.classList.contains('table-el-el-descriptions__table') || container.classList.contains('route-process')) {
        tableRender = new descriptionsTable(container);
    }else if (container.classList.contains('table-el-el-descriptions__card')) {
        tableRender = new dataCardRenderer(container);
    }else if (container.classList.contains('post-table')) {
        tableRender = new postTableRenderer(container);
    }else if (container.classList.contains('el-select__inner')){
        tableRender = new selecterRenderer(container)
    }
    else{
      tableRender = new tableRenderer(container)
    }    
    tableRender.toggleLoad = isToggleLoad;
    tableRender.method = method;
    data = data != null ? data : method === 'GET' ? data : (tableRender?.getData() ?? [])
    if (method==='POST' && data?.length == 0) return
    await fetchDataRenderFrame(tableRender, method, data);
}

export function handleTableEvent(container)
{
    container.addEventListener('click', e => {
        if (e.target.matches('a.pager-btn')) {
            const table = e.target.parentNode.previousElementSibling;
            new TablerHandler(table).pageLoad(e.target);
            e.preventDefault(); 
        }
        if (e.target.matches('#add-row')) {
            const table = e.target.parentNode.previousElementSibling;
            new TablerHandler(table).addRow()}
        if (e.target.matches('#remove-row')) {
            new TablerHandler(container.querySelector('table')).deleteRow(e.target.closest("tr"))}
        if (e.target.matches('#submit')) {
            let table = e.target.parentNode.previousElementSibling;
            table = table.nodeName =='TABLE'? table: table.querySelector('table')
            //const tableHandler = new TablerHandler(table, 'POST');
            //tableHandler.update(table.querySelector("tbody"));
            renderFrameAndLoadData(table, 'POST',  null, true)
        }
        if (e.target.matches('#updata')) {
            new TablerHandler(container.querySelector('table'), 'PUT').update(e.target.closest("tr"))}
        if (e.target.matches('select')) {
            const selecterRender = new selecterRenderer(e.target)
            fetchDataRenderFrame(selecterRender)} 
        if (e.target.matches('input')) {            
            let table = e.target.closest('table')
            new TablerHandler(table, 'GET').getDataByUniqKey(e.target)}
        if (e.target.matches('#quick-fill')){
            const model = document.getElementById('quick-fill-modal')
            utils.switchOverlay(model, true)
        }
    });
}

class fastFillModelHandler{
    constructor(container)
    {
        this.container = container;
        this.selector = container.querySelector('select')
        this.table = container.querySelector('table')
        this.hiddenTextarea = container.querySelector('#hidden-paste-area');
    }
    selectedChange(){
        if (!this.selector || !this.table) return;   
        const option = JSON.parse(this.selector.dataset.option)     
        const key = option.key;
        const val = this.selector.value;
        const params = (key && val && key.trim() && val.trim()) 
            ? { [key]: val } 
            : {};
        
        this.table.dataset.baseData = JSON.stringify(params);        
    }
    async update() {
        if (this.selector && !this.selector.checkValidity()) return alert('请选择新增属性类别后重试');
        const tabler = new TablerHandler(this.table, 'POST')
        await tabler.submitDataAndPost()
    }
    static handlePaste(event, table) {
        event.preventDefault();

        const clipboardData = event.clipboardData || window.clipboardData;
        if (!clipboardData) return;
        
        const pastedData = clipboardData.getData('text');
        if (!pastedData) return;
        const rows = pastedData.split(/\r\n|\n|\r/).filter(row => row.trim());
        if (rows.length === 0) return;
        const tableRender = new postTableRenderer(table)
        tableRender.pastedData(rows) 
        console.log(`成功粘贴 ${rows.length} 行数据`);
    }
}


export function handleFastFillModelEvent(container,submitHandler = null)
{
    container.addEventListener('click', e => {
        if (e.target.matches('#submit')) {
            if (submitHandler) {
                try {
                    submitHandler(e);
                }
                catch (error) {
                    console.error('Submit handler error:', error);
                }
            }else{
                const tableHandler = new fastFillModelHandler(container);
                tableHandler.update();
            }
        }
        if (e.target.matches('select')) {
            const selecterRender = new selecterRenderer(e.target)
            fetchDataRenderFrame(selecterRender)} 
        if (e.target.matches('#switch-modal')) 
            utils.switchOverlay(container, false);
        if (e.target.matches('#maximize-modal')) 
            utils.maximizeModal(container, 'main');
    });
    container.addEventListener('change', e => {
        if (e.target.matches('select')){
            new fastFillModelHandler(container).selectedChange()        
        }
    })
    container.addEventListener("paste", function (event) {        
        fastFillModelHandler.handlePaste(event, container.querySelector('table'))   
    })
}

export function handlePostTableEvent(container, additionalHandler = null)
{
    container.addEventListener('click', e => {
        if (e.target.matches('#add-row')) {
            const table = e.target.parentNode.previousElementSibling;
            new TablerHandler(table).addRow()}
        else if (e.target.matches('#remove-row')) {
            new TablerHandler(container.querySelector('table')).deleteRow(e.target.closest("tr"))}
        else if (e.target.matches('#submit')) {
            let table = container.querySelector('table')
            const tabler = new TablerHandler(table, 'POST')
            tabler.submitDataAndPost()
        }
        else if (e.target.matches('#quick-fill')){
            const model = document.getElementById('quick-fill-modal')
            utils.switchOverlay(model, true)
        } 
        else if (e.target.matches('select')) 
            if(e.target.dataset.url) renderFrameAndLoadData(e.target)
        if (additionalHandler) {
            try {
                additionalHandler(e);
            }
            catch (error) {
                console.error('Additional handler error:', error);
            }
        }
    });
    container.addEventListener('change', e => {
        if (e.target.matches('#uniq_input')) {
            const table = e.target.closest('table');
            if (table) {
                new TablerHandler(table, 'GET').getDataByUniqKey(e.target);
            }
        }
    });
}

export function handleResultListEvent(table)
{
    table.addEventListener('click', e => {
        if (e.target.matches('#change')) {
            const tbHander = new TablerHandler(container.querySelector('table'), 'PUT', true);
            tbHander.update(e.target.closest("tr"))
        }

    });
}
