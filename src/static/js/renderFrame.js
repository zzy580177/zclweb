import {utils, URLConfig} from './utils.js';
import {H_ENDPOINTS, K_ENDPOINTS, T_ENDPOINTS, BUTTON_NAME2ID, API_CONFIG} from './apiConfig.js';

const MIDPART_INFO = {id:'207', name:'中间件'}

export class BaseRenderer {
    static clearContainer(container) {
        container.innerHTML = '';
    }

    static showError(container, message) {
        container.innerHTML = `<div class="error">${message}</div>`;
    }

    static validateParams(container, data, defHtml = '<p class="p-4">无可用数据</p>') {
        if (!container) return false;
        if (!Array.isArray(data) || !data.length) {
            container.innerHTML = defHtml;
            return false;
        }
        return true;
    }
}

export class dataCardRenderer {
    constructor(table, params = null) {
        this.table = table;
        this.params = table? utils.datasetToObj(table) : params;
        this.headers = JSON.parse(this.params?.headers || '[]');
        this.keys = JSON.parse(this.params?.keys || '[]');  
        this.url = JSON.parse(this.params?.url || '{}')
        this.endpoint = this.url?.endpoint || '';
        this.url_params = this.url.params || '{}';
        this.data = [];
        this.thead = table?.querySelector('thead');
        this.tbody = table?.querySelector('tbody');
        this.method = 'GET'
        if(this.table){       
            this.table.className = 'el-descriptions__card';
            this.table.style.width = '100%';
            this.table.style.borderCollapse = 'collapse';
            //this.id = this.table.id;
        }
        this.maxColumn = 4
    }
    render(result) {
        const data = result?.data?.items || result;
        if(!BaseRenderer.validateParams(this.table, data)){
            return;
        } 
        this.table.appendChild(document.createElement('thead'))
        const tbody = document.createElement('tbody')
        for (let i = 0; i < this.headers.length; i += this.maxColumn) {
            const [labelRow, valueRow] = this.buildCardRows(data[0], i);
            tbody.append(labelRow, valueRow);
        }
        this.table.appendChild(tbody)
    }
    buildCardRows(dataItem, startIdx) {
        const labelRow = document.createElement('tr');
        const valueRow = document.createElement('tr');
        
        for (let j = startIdx; j < startIdx + this.maxColumn && j < this.headers.length; j++) {
            labelRow.innerHTML += `
                <td><div><span class="el-descriptions-item__label">
                    ${this.headers[j]}
                </span></div></td>`;
            
            valueRow.innerHTML += `
                <td><div><span class="el-descriptions-item__content">
                    ${utils.getValueByPath(dataItem, this.keys[j], '-')}
                </span></div></td>`;
        }
        
        return [labelRow, valueRow];
    }
}

export class tableRenderer{
    constructor(table, params=null) {
        this.table = table;
        this.params = table? utils.datasetToObj(table) : params || {};
        this.headers = JSON.parse(this.params?.headers || '[]');
        this.keys = JSON.parse(this.params?.keys || '[]');
        this.hidkeys = JSON.parse(this.params?.hidkeys || '[]');
        this.inputs = JSON.parse(this.params?.inputs || '[]');
        this.numbers = JSON.parse(this.params?.numbers || '[]');
        this.uniqKeys = JSON.parse(this.params?.uniqKeys || '[]');
        this.require = JSON.parse(this.params?.require || '[]');        
        this.selects = JSON.parse(this.params?.selects || '[]');     
        this.inputdates= JSON.parse(this.params?.dates || '[]');     
        this.buttons = JSON.parse(this.params?.buttons || '[]');
        this.limit = JSON.parse(this.params?.limit || 0);
        this.page = JSON.parse(this.params?.page || 1);
        this.url = JSON.parse(this.params?.url || '{}')
        this.endpoint = this.url?.endpoint ||this.params.endpoint || '';
        this.url_params = this.url?.params|| {};
        this.data = [];
        this.thead = table?.querySelector('thead');
        this.tbody = table?.querySelector('tbody');
        this.method = 'GET'
        this.minrows = 1;
        if(this.limit > 0){
            this.url_params.limit = this.limit
            this.url_params.page = this.page
        }
    }
    setMinRows(minrows){
        this.minrows = minrows
    }
    postRender(result){
        if(!result) return
        alert(result.message || '数据上传成功!');
        const rows = this.tbody.querySelectorAll('tr');
        rows.forEach(row => {
            Array.from(row.cells).forEach(cell => {
                const input = cell.querySelector('input');
                if (input) {
                    input.style.backgroundColor = ''; 
                    input.value = '';
                }
            });
        });
        return
    }
    postRenderError(response) {
        const errorMessage = [response?.message, 
            Array.isArray(response?.Error) ? response.Error.join('\n') : ''
        ].filter(Boolean).join('\n\n') || '发生未知错误';
        alert(errorMessage);

        if (Array.isArray(response?.faileds) && response.faileds.length > 0) {
            const rows = this.tbody.querySelectorAll('tr');
            const failedRowIdxs = response.faileds.map(failed => failed.id);
            response.faileds.forEach(failed => {
                const row = rows[failed.id];
                if (row) {
                    const cell = Array.from(row.cells).find(td => td.dataset.key === failed.key);
                    if(cell) {
                        const input = cell.querySelector('input');
                        if (input) input.style.backgroundColor = '#ffcccc';
                    }
                }
            });
            rows.forEach((row, idx) => {
                if(!failedRowIdxs.includes(idx)) row.remove(); 
            });  
        }  
    }
    renderNewRow(data){
        if(!this.table.querySelector('thead')) {
            this.render({items:[data]});
        }
        else if(!this.tbody){
            this.data = [data];
            this.createBody()
        }else{
            const tr = this.createRow(data);
            this.tbody.appendChild(tr);
        }
    }
    getResponeData(result){
        this.data = (result.data && (result.data.items || result)) || [];  // 默认空数组
    }
    render(result) {
        if(this.method !== 'GET') return this.postRender(result)
        BaseRenderer.clearContainer(this.table);
        this.clearPageination();
        this.getResponeData(result);
        this.total_count = (result && result.count) || 0;        // 默认0
        if(!BaseRenderer.validateParams(this.table, this.data)){
            return;
        } 
        
        this.createHeader();
        if(this.params['groupkey']) this.createTreeBody(this.params['groupkey']);
        else this.createBody();
        if(this.url_params.limit > 0 && this.total_count > 0) this.createPagination(this.total_count, this.page)
    }
    renderError(response) {
        response = response.data || response;
        if(this.method !== 'GET') return this.postRenderError(response)
        BaseRenderer.showError(this.table, response);
    }
    createHeader(className = '') {
        if (!this.table || !this.headers || this.headers.length === 0) return;
        this.thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        headerRow.style.fontWeight = 'bold';
        this.headers.forEach(header => {
            const th = document.createElement('th');
            if(className && className !== '')
                th.className = className;
            th.textContent = header;
            headerRow.appendChild(th);
        });
        this.thead.appendChild(headerRow);
        this.table.appendChild(this.thead);
    }
    setTdtype(key, val){
        const request = this.require.includes(key)
        if(this.buttons.includes(key)) {
            return {type: 'button', required: request};
        }
        if(this.inputs.includes(key)) {
            return {type: 'input', required: request};
        }
        if(this.selects[key]!== undefined) {
            return {type: 'select', required: request};
        }
        if(this.inputdates.includes(key)) {
            return {type: 'inputdate', required: request};
        }
        return Array.isArray(val)? {type: 'div', required: request}:{type: 'td', required: request};
    }
    getValueByPath(obj, path, fallback = '-') {
        return utils.getValueByPath(obj, path, fallback);
    }
    createButtonForCell(key)
    {
        const button = document.createElement('button');
        button.textContent = key;
        button.id = BUTTON_NAME2ID[key];
        button.className = 'el-button el-button--warning el-button--small';
        return button
    }    
    createInputForCell(cell, val, request, key)
    {
        const input = document.createElement('input');
        input.id = this.uniqKeys.includes(key)? 'uniq_input':'';
        input.className = 'optimized-width';
        input.type = 'text';
        if(this.numbers.includes(key)){
            input.type = 'number';
        }
        input.value = val;
        input.required = request;        
        cell.appendChild(input);
    }
    createDateInput(cell, val, request, key)
    {
        const input = document.createElement('input');
        input.className = 'optimized-width';
        input.type = 'date';
        if(val && !isNaN(Date.parse(val))){
            const date = new Date(val);
            // 设置为 yyyy-mm-dd 格式，兼容 input[type=date]
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            input.value = `${year}-${month}-${day}`;
        }
        input.required = request;        
        cell.appendChild(input);
    }

    createSelectForCell(cell, request, key, val, item = null) {
        const selDef = (this.selects && this.selects[key]) ? this.selects[key] : null;

        let optionals = [];
        const dataKey = selDef.dataK || '';
        if (item && dataKey && Object.prototype.hasOwnProperty.call(item, dataKey)) {
            const v = item[dataKey];
            optionals = Array.isArray(v) ? v : (v != null ? [v] : []);
        } else if (selDef && Array.isArray(selDef.datas)) {
            optionals = selDef.datas;
        } else {
            optionals = [];
        }

        const render = new selecterRenderer(null, selDef);
        render.render(optionals);
        render.updateSelected(val);
        
        render.selecter.className = 'optimized-width';
        render.selecter.required = request;

        cell.appendChild(render.selecter);
    }
    renderRow(data, rowIdx){
        if (this.tbody.rows && this.tbody.rows.length > rowIdx-1) {
            const tr = this.tbody.rows[rowIdx-1];
            const cells = tr.querySelectorAll('td')
            cells.forEach(cell =>{
                let key = cell.dataset.key
                if(key){
                    const cell_child = cell.firstChild
                    if(cell_child.nodeName  == 'INPUT')
                    {
                        cell_child.value = data.items[0][key]||''
                    }
                    if(cell_child.nodeName  == 'SELECT')
                    {
                        key = cell_child.dataset.key
                        const val = data.items[0][key]
                        if(key && val && Array.isArray(val)){
                            new selecterRenderer(cell_child).render(val)
                            cell_child.dataset.datas = JSON.stringify(val)
                        }
                    }
                }
            })
        }
    }
    createCell(val, key, item=null) {
        const tdType = this.setTdtype(key, val);
        const cellType = tdType.type;
        const request = tdType.required;
        const cell = document.createElement('td');
        cell.setAttribute('data-key', key.split('.').at(-1));
        if (this.hidkeys.includes(key)) {
            cell.style.display = 'none';
        }
        switch (cellType) {
            case 'inputdate':
                this.createDateInput(cell, val, request, key);
                break;
            case 'input':
                //cell.contentEditable  = true;
                //cell.textContent = val;
                this.createInputForCell(cell, val, request, key);
                break;
            case 'select':
                this.createSelectForCell(cell, request, key, val, item);
                break;
            case 'button':
                cell.appendChild(this.createButtonForCell(key));
                break;
            case 'div':
                cell.style.whiteSpace = 'nowrap';
                val.forEach(v => {
                    const div = document.createElement('div');
                    div.textContent = v;
                    cell.appendChild(div);
                });
                break;
            case 'td':
                cell.contentEditable  = true;
            default:
                cell.textContent = val;
                cell.className = 'el-table__cell';
                break;
            }
        return cell;
    }
    createRow(item) {
        if (!this.table || !this.keys || this.keys.length === 0) return null;
        const row = document.createElement('tr');
        if(item){
            this.keys.forEach(key => {
                const val = item[key] ? item[key] : this.getValueByPath(item, key, '-');
                row.appendChild(this.createCell(val,key,item));});
        }else if(this.minrows > 0){
            this.keys.forEach(key => {row.appendChild(this.createCell('',key));});
        }
        return row;
    }    
    updateRow(row, item){
        if (!row ||!this.table || !this.keys || this.keys.length === 0) return null;
        if (!item) return null;
        row.innerHTML = ''
        this.keys.forEach(key => {
            const val = item[key] ? item[key] : this.getValueByPath(item, key, '-');
            row.appendChild(this.createCell(val,key));
        });
    }
    createBody(){
        if (!this.table || !this.keys || this.keys.length === 0) return;
        this.tbody = document.createElement('tbody');
        if(Array.isArray(this.data)&&(this.data.length > 0)){             
            this.data.forEach(item => {this.tbody.appendChild(this.createRow(item));});
        }else{
            this.tbody.appendChild(this.createRow())
        }
        this.table.appendChild(this.tbody);
    }
    createTreeBody(parentKey='order_id') {
        if (!this.table || !this.keys || this.keys.length === 0) return;
        this.tbody = document.createElement('tbody');
        let groupedData = {};
        this.data.forEach(item => {
            const parentId = this.getValueByPath(item, parentKey, '未知');
            if (!groupedData[parentId]) {
                groupedData[parentId] = [];
            }
            groupedData[parentId].push(item);
        });
        Object.entries(groupedData).forEach(([parentId, items]) => {
            const parentRow = document.createElement('tr');
            parentRow.className = 'parent-row';
            parentRow.style.backgroundColor = '#f0f0f0';
            parentRow.style.cursor = 'pointer';
            const parentCell = document.createElement('td');
            parentCell.colSpan = this.keys.length;
            parentCell.textContent = `${parentKey}: ${parentId} （点击展开/收起）`;
            parentRow.appendChild(parentCell);
            this.tbody.appendChild(parentRow);
            items.forEach(item => {
                const childRow = this.createRow(item);
                if (childRow) {
                    childRow.className = 'child-row';
                    childRow.style.display = 'none';
                    this.tbody.appendChild(childRow);
                }
            });
            parentRow.addEventListener('click', () => {
                const isVisible = parentRow.classList.toggle('expanded');
                items.forEach((_, index) => {
                    const childRow = this.tbody.children[this.tbody.children.length - items.length + index];
                    if (childRow) {
                        childRow.style.display = isVisible ? '' : 'none';
                    }
                });
            });
        });
        this.table.appendChild(this.tbody);
    }
    clearPageination() {
        let pager = this.table.nextElementSibling;
        if (pager && pager.classList && pager.classList.contains('table-pager')) {
            while (pager.firstChild) {
                pager.removeChild(pager.firstChild);
            }
        }
    }
    createPagination(total, page = 1) {
        let pager = this.table.nextElementSibling;
        if (!pager || !pager.classList.contains('table-pager')) {
                pager = document.createElement('div');
                pager.className = 'table-pager';
                pager.style = 'margin:10px 0;text-align:center;';
                this.table.parentNode.insertBefore(pager, this.table.nextSibling);
        }
        const totalPages = Math.max(1, Math.ceil(total / this.limit));
        this.page = Math.max(1, Math.min(page, totalPages));

        let html = `共 ${total} 条 `;

        if (this.page > 1) html += `<a href="#" data-page="${this.page - 1}" class="pager-btn">&lt;</a>`;
        else html += `<span class="pager-btn pager-disabled">&lt;</span>`;

        let start = Math.max(1, this.page - 2);
        let end = Math.min(totalPages, this.page + 2);
        if (this.page <= 3) end = Math.min(5, totalPages);
        if (this.page >= totalPages - 2) start = Math.max(1, totalPages - 4);

        if (start > 1) {
            html += `<a href="#" data-page="1" class="pager-btn">1</a>`;
            if (start > 2) html += `<span class="pager-ellipsis">...</span>`;
        }
        for (let i = start; i <= end; i++) {
            if (i === this.page)  html += `<b class="pager-btn pager-current">${i}</b>`;
            else html += `<a href="#" data-page="${i}" class="pager-btn">${i}</a>`;
        }
        if (end < totalPages) {
            if (end < totalPages - 1) html += `<span class="pager-ellipsis">...</span>`;
            html += `<a href="#" data-page="${totalPages}" class="pager-btn">${totalPages}</a>`;
        }

        if (this.page < totalPages)  html += `<a href="#" data-page="${this.page + 1}" class="pager-btn">&gt;</a>`;
        else  html += `<span class="pager-btn pager-disabled">&gt;</span>`;

        html += `&nbsp;前往 <input type="number" min="1" max="${totalPages}" value="${this.page}" class="pager-input" style="width:40px;text-align:center;"> 页`;

        pager.innerHTML = html;
    }
    getData(){
        this.data = []
        const rows =  this.tbody.querySelectorAll('tr');
        rows.forEach( row => this.data.push(this.getTrData(row)))
        return this.data
    }
    getTrData(row){
        if(!row) return
        const rawData = Object.assign({}, this.baseData)
        const tds = row.getElementsByTagName('td');
        Array.from(tds).forEach(td => {
            if(!td.querySelector('button')) {
                const divs = td.querySelectorAll('div');
                const key = td.dataset.key;                
                if(divs.length > 0) {
                    rawData[key] = Array.from(divs).map(div => div.textContent.trim());
                } else {
                    rawData[key] = td.firstChild ? 
                        (td.firstChild.value || td.firstChild.textContent.trim()) : 
                        td.textContent.trim();
                }
                if(this.numbers.includes(key))
                    rawData[key] = parseInt(rawData[key])
            }
        });
        return rawData;
    }
}

export class selecterRenderer{
    constructor(selecter = null, params = null) {
        this.params = selecter ? utils.datasetToObj(selecter): params;
        this.url = (typeof this.params.url === "object")? this.params.url||{} :JSON.parse(this.params?.url ||'{}')  
        this.option = (typeof this.params.option === "object")? this.params.option||{} : JSON.parse(this.params?.option ||'{}')       
        this.endpoint = this.params?.endpoint || this.url?.endpoint || ''   
        this.default = document.createElement('option');
        this.default.value = "";
        this.default.textContent = this.option.defaultText || '请选择';
        //this.url_params = this.params?.url_params ? JSON.parse(this.params.url_params) : {};
        this.selecter = selecter? selecter : document.createElement('select');
        this.selectedValue = this.selecter?.value || '';
        this.isBefore = this.selecter?.classList.contains('before') || false;
        this.isAfter = this.selecter?.classList.contains('after') || false;
    }
    render(result) {
        if(this.isBefore) {
            if(this.isAfter){
                this.selecter.classList.remove('after');
                this.selecter.classList.remove('before');
            }
            return;
        }
        BaseRenderer.clearContainer(this.selecter);
        this.selecter.className = 'el-select__inner';
        this.selecter.value = this.selectedValue || '';
        const data = result?.data?.items ?? result ?? [];
        this.options = [this.default];
        if (Array.isArray(data) && data.length > 0) {
            data.forEach(item => {
                const option = document.createElement('option');
                option.value = utils.getValueByPath(item, this.option?.key || 'id', '');
                option.textContent = this.option?.textK ? utils.getValueByPath(item, this.option.textK, '' ) 
                : `${this.option.optionText ||''} ${option.value}`;
                this.options.push(option);
            });
            this.selecter.classList.toggle('before', true);
        }
        this.selecter.append(...this.options);
    }
    static appendOptionV(selecter, value, text) {
        if (!selecter) return false; // 防御性检查
        
        const exists = Array.from(selecter.querySelectorAll('option'))
            .some(option => option.value === value);
        
        if (!exists) {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = text;
            selecter.append(option);
        }
    }
    static change(selecter)
    {
        selecter.classList.toggle('after', true);
    }
    updateSelected(value) {
        const hasValue = this.options.some(opt => 
            typeof opt === 'object' ? opt.value == value : opt == value
        );
        if (hasValue) {
            this.selecter.selected = true;
            this.selecter.value = value;
        }
    }
    getValue() {
        return this.selecter.value;
    }
}
export class transferRenderer{
    constructor(transfer = null) {
        this.transfer = transfer
        this.params = utils.datasetToObj(this.transfer);
        this.url_params = JSON.parse(this.params?.url_params || '{}');
        this.url = JSON.parse(this.params?.url ||'{}')  
    }
    render(result) {
        BaseRenderer.clearContainer(this.transfer)
        const data = result.items || result
        if(!BaseRenderer.validateParams(this.transfer, data)){
            return;
        } 
        data.forEach(obj => {
            const div = document.createElement('div');
            div.className = 'step-item';            
            if(obj.material_id){
                div.textContent = obj.material_model;
                div.dataset.id = MIDPART_INFO.id;
                div.dataset.name = MIDPART_INFO.name;
                div.dataset.type_name = MIDPART_INFO.name;
                div.dataset.params = obj.material_model;
                div.dataset.material_id = obj.material_id; }
            else{        
                div.textContent = obj.name;     
                div.dataset.id = obj.id;     
                div.dataset.name = obj.name;
                div.dataset.type_name = obj.type_name;
                div.dataset.params = '';
            }
            this.transfer.appendChild(div);
        });
    }
}

export class postTableRenderer extends tableRenderer{
    constructor(table, rowCount = 6){
        super(table);
        this.table.classList.add('post-table');
        this.baseData = JSON.parse(table.dataset.baseData??'{}');
        this.numbers = JSON.parse(table.dataset.numbers??'[]');
        this.rowCount = rowCount
    }
    initiTable(rowCount = this.rowCount){
        this.rowCount = rowCount;
        BaseRenderer.clearContainer(this.table);
        this.createHeader();
        this.createBody(rowCount);
    }
    createBody(){
        if (!this.table || !this.rowCount || !this.keys || this.keys.length === 0) return;
        this.tbody = this.tbody? this.table.querySelector('tbody') : document.createElement('tbody');
        this.tbody.innerHTML = ''
        for(let i = 0; i < this.rowCount; i ++ )
        {
            this.tbody.appendChild(this.createRow())
        }
        this.table.appendChild(this.tbody);
    }
    pastedRow(item) {
        if (!this.table || !this.keys || this.keys.length === 0) return null;
        const row = document.createElement('tr');
        for(let i = 0; i < this.keys.length; i++){
            row.appendChild(this.createCell(item[i]||'',this.keys[i]));
        }
        return row;
    } 
    pastedData(data){
        this.inputs = this.keys
        this.tbody.innerHTML = '';
        data.forEach(row => {
            if (!row.trim()) return;
            const cells = row.split('\t');
            this.tbody.appendChild(this.pastedRow(cells))
        })
    }

    postRender(result){
        if(!result) return
        alert(result.message || '数据上传成功!');        
        this.createBody(this.rowCount);
        return
    }
}

export class floatingWindModelRender
{
    initialize(result) {
        this.container.innerHTML = '';
        this.createHeader();
        this.createLine();
        this.createExtra();
        this.createBody();
        this.createFooter();
        this.randerSelecter();
        this.randerTableData();
    }
    constructor(container, table_params=null, select_params=null, button_group=null) {
        this.container = container;
        this.title = container.getAttribute('data-title') || '';
        this.select_params = select_params || {}
        this.table_parmer = table_params || {}
        this.button_group = button_group
        this.extraDiv = container.querySelector('.el-descriptions__extra');
        this.selecter = container.querySelector('.el-descriptions__extra select');
        this.footerDiv = container.querySelector('.el-descriptions__footer');
        this.tableDiv = container.querySelector('.el-descriptions__body table');
        this.table_id = this.table_parmer?.id || '';
    }
    
    createHeader()
    {
        const header = document.createElement('div');
        header.className = 'el-descriptions__header';
        const titleDiv = document.createElement('div');
        titleDiv.className = 'el-descriptions__title';
        titleDiv.textContent = this.title || '';
        header.appendChild(titleDiv);
        
        if(this.container.classList.contains('has-hide-swc-button')) {
            const hideSwcBtn = document.createElement('button');
            hideSwcBtn.innerHTML = '<i class="fas fa-chevron-up" id="collapseIcon"></i><span>收起内容</span>'
            hideSwcBtn.id = 'hide_process'
            hideSwcBtn.className = 'collapse-btn'
            hideSwcBtn.style.backgroundColor = '#2f7deb'
            header.appendChild(hideSwcBtn);
        }
        this.container.appendChild(header); 
    }
    createLine(background = '#2f7deb')
    {
        const line = document.createElement('div');
        line.className = 'el-descriptions__line';
        line.style.height = '1px';
        line.style.background = background;
        line.style.borderRadius = '1px';
        line.style.margin = '8px 0';
        this.container.appendChild(line);
    }

    createExtra(container = this.container)
    {        
        if(!this.select_params || Object.keys(this.select_params).length === 0) return null;
        const extraDiv = document.createElement('div');
        extraDiv.className = 'el-descriptions__extra';
        extraDiv.style.marginBottom = '20px';
        extraDiv.style.marginTop = '5px';
        extraDiv.style.display = 'flex';
        extraDiv.style.gap = '10px';
        this.selecter = document.createElement('select')         
        this.selectedContext = document.createElement('div')         
        this.selectedContext.id = 'select-help-note'   
        extraDiv.appendChild(this.selecter);
        extraDiv.appendChild(this.selectedContext);   
        this.extraDiv = extraDiv;
        container.appendChild(extraDiv);
        this.selecter.required = this.select_params.required || false
        utils.setDataset(this.selecter, this.select_params)
    }

    createBody(container = this.container)
    {                
        const body = document.createElement('div');
        body.className = 'el-descriptions__body';
        const table = document.createElement('table');
        table.className = this.container.classList.contains('card') ? 'table-el-el-descriptions__card' : 'table-el-el-descriptions__table';
        table.id = this.table_id;
        body.appendChild(table);
        this.tableDiv = table;
        container.appendChild(body);
        utils.setDataset(this.tableDiv, this.table_parmer)
    }
    createFooter(container = this.container)
    {
        const footerDiv = document.createElement('div');
        footerDiv.className = 'el-descriptions__footer';
        footerDiv.style.marginBottom = '20px';
        footerDiv.style.marginTop = '20px';
        this.footerDiv = footerDiv;
        if(this.button_group && Object.keys(this.button_group).length > 0){
            this.renderButtonGroup();
        }
        container.appendChild(footerDiv);
    }

    renderButtonGroup()  // fmdoel is not used, but kept for compatibility
    {
        const buttonContainer = document.createElement('div');
        buttonContainer.style.marginTop = '10px';
        buttonContainer.style.textAlign = 'right';
        buttonContainer.style.display = 'flex';

        this.button_group.forEach(btnInfo => {
            const button = document.createElement('button');
            button.id = btnInfo.id || '';
            button.className = btnInfo.className || 'el-button el-button--primary el-button--small';
            button.textContent = btnInfo.text || '按钮';
            buttonContainer.appendChild(button);
        });
        this.footerDiv.appendChild(buttonContainer);
    }
    randerTableData()
    {
        new postTableRenderer(this.tableDiv).initiTable();   
    }
    randerSelecter()
    {
        if(this.selecter){
            const selecterRender = new selecterRenderer(this.selecter)
            selecterRender.render(); 
        }  
    }
}

export class fastFillModelRenderer extends floatingWindModelRender
{
    constructor(container, select_params, table_params, button_group = [{id: 'submit', text: '确认', className: 'el-button el-button--warning el-button--small'}])
    {
        super(container, table_params, select_params, button_group)
    }
    initialize(result) {
        this.container.innerHTML = '';
        this.createLine();
        this.createExtra();
        this.renderHelpNotes();
        this.createHiddenTextarea()
        this.createBody();
        this.createFooter();
        this.randerSelecter();
        this.randerTableData(result?.items || result);
        this.textarea.focus()
    }

    renderHelpNotes() {
        const notediv = document.createElement('div')
        const notep = document.createElement('p')
        notediv.className = 'modal-description'
        notep.style.display = 'block'
        notep.style.width = '100%'
        notep.style.margin = '10px 0'
        notep.style.whiteSpace = 'pre-line'
        notep.textContent = '可将 Excel 内容粘贴到表格中，也可直接编辑表格内容，支持使用复制、粘贴、撤销、删除快捷键。'
        notediv.appendChild(notep)
        this.container.appendChild(notediv)
    }

    createHiddenTextarea(id = 'hidden-paste-area') {
        let textarea = document.createElement('textarea');
        textarea.id = id;
        textarea.style.position = 'absolute';
        textarea.style.left = '-9999px';
        textarea.style.top = '0';
        textarea.style.width = '1px';
        textarea.style.height = '1px';
        textarea.style.opacity = '0';
        textarea.setAttribute('tabindex', '-1');
        this.textarea = textarea;
        this.container.appendChild(textarea)
    }
}

export function handleToggleButton(container, button) {
        const isExpanded = button.dataset.expanded === 'true';
        if (isExpanded) {
            // 收起
            button.innerHTML = '<i class="fa fa-chevron-right"></i> 展开';
            button.dataset.expanded = 'false';
            container.style.display = 'none';
        } else {
            // 展开
            button.innerHTML = '<i class="fa fa-chevron-down"></i> 收起';
            button.dataset.expanded = 'true';
            container.style.display = 'block';
        }
}
