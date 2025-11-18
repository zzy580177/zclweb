import {utils, URLConfig} from './utils.js';
import {H_ENDPOINTS, K_ENDPOINTS, T_ENDPOINTS, BUTTON_NAME2ID, API_CONFIG} from './apiConfig.js';

class BaseRenderer {
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



export class partDescriptions
{
    renderSubRoute(data) {
        this.container.innerHTML = '';
        this.createLine('#0d47a1');
        this.createHeader()
        this.createExtra();
        this.createBody();
        this.createFooter();
        this.renderButtonGroupForEdit();
        this.randerEmptySelecter();
        this.randerTableData(data);
    }

    render(result) {
        this.container.innerHTML = '';
        this.createHeader();
        this.createLine();
        this.createExtra();
        this.createBody();
        this.createFooter();
        this.renderButtonGroupForEdit();
        this.randerEmptySelecter();
        this.randerTableData(result?.items || result);
    }

    randerTableData(result)
    {
        const title = this.title.includes('工艺线路')? '工艺线路': this.title;
        const params = {
            'headers': JSON.stringify(H_ENDPOINTS['pmcui-porder'][title]||[]),
            'keys': JSON.stringify(K_ENDPOINTS['pmcui-porder'][title]||[]),
            'url': JSON.stringify(API_CONFIG['pmcui-porder'][title].path),
            'url_params': JSON.stringify(URLConfig.buildApiParams('pmcui-porder',title, this.orderPart)),
            'orderPart': JSON.stringify(this.orderPart),
            'buttons': this.title.includes('工艺线路')? JSON.stringify(['编辑']): '[]'
        } 
        utils.setDataset(this.tableDiv, params)
        const tableRender = this.bodyType === 'table'? 
            new descriptionsTable(this.tableDiv) : new descriptionsCard(this.tableDiv);
        tableRender.render(result);   
    }
    randerEmptySelecter()
    {
        if(this.selecter){
            const params = {
                optionText: '工艺线路',
                defaultText: '请选择历史工艺线路设计',
                key: 'Id',
                url: JSON.stringify(API_CONFIG['pmcui-porder'].route_get), 
                url_params: JSON.stringify({'FId': this.orderPart['FId']})}
            utils.setDataset(this.selecter, params)
            const selecterRender = new selecterRenderer(this.selecter)
            selecterRender.render(); 
        }  
    }

    constructor(container, part_data) {
        this.modal = document.getElementById('parts-detail-modal');
        this.params = utils.datasetToObj(this.modal); // Fixed reference
        this.container = container;
        this.title = container.getAttribute('data-title') || '';
        this.issubPart = container.dataset['isSubPart'] === 'true';
        this.orderPart = part_data? part_data : JSON.parse(this.params.orderPart||'{}')
        this.bodyType = this.container.dataset.body?? 'card'
        this.hasSelecter = this.container.dataset.select?? 'none'
        this.extraDiv = container.querySelector('.el-descriptions__extra');
        this.selecter = container.querySelector('.el-descriptions__extra select');
        this.footerDiv = container.querySelector('.el-descriptions__footer');
        this.tableDiv = container.querySelector('.el-descriptions__body table');
    }
    
    createHeader()
    {
        const header = document.createElement('div');
        header.className = 'el-descriptions__header';
        const titleDiv = document.createElement('div');
        titleDiv.className = 'el-descriptions__title';
        titleDiv.textContent = this.title || '';
        header.appendChild(titleDiv);
        if(this.title == '工艺线路'){
            const hideSwcBtn = document.createElement('button');
            hideSwcBtn.innerHTML = '<i class="fas fa-chevron-up" id="collapseIcon"></i><span>收起内容</span>'
            hideSwcBtn.id = 'hide_process'
            hideSwcBtn.className = 'collapse-btn'
            hideSwcBtn.style.backgroundColor = '#2f7deb'
            header.appendChild(hideSwcBtn);
        }
        this.container.appendChild(header); 
        if(this.title.includes('工艺线路')) {
            this.title = '工艺线路'; 
        }
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
    createExtra()
    {
        if(this.hasSelecter === 'none' ) return null;
        const extraDiv = document.createElement('div');
        extraDiv.className = 'el-descriptions__extra';
        extraDiv.style.marginBottom = '20px';
        extraDiv.style.marginTop = '20px';
        extraDiv.style.display = 'flex';
        extraDiv.style.gap = '10px';
        this.selecter = document.createElement('select')         
        //this.selecter.style.display ='inline-flex'       
        this.selectedContext = document.createElement('div')         
        this.selectedContext.id = this.hasSelecter
        //this.selectedContext.style.display ='inline-flex'     
        extraDiv.appendChild(this.selecter);
        extraDiv.appendChild(this.selectedContext);   
        this.extraDiv = extraDiv;
        this.container.appendChild(extraDiv);
    }

    createBody()
    {                
        const body = document.createElement('div');
        body.className = 'el-descriptions__body';
        const table = document.createElement('table');
        table.id = `${T_ENDPOINTS[this.title]||''}-${this.orderPart['FModel']||''}`;
        body.appendChild(table);
        this.tableDiv = table;
        this.container.appendChild(body);
    }
    createFooter()
    {
        const footerDiv = document.createElement('div');
        footerDiv.className = 'el-descriptions__footer';
        footerDiv.style.marginBottom = '20px';
        footerDiv.style.marginTop = '20px';
        this.footerDiv = footerDiv;
        this.container.appendChild(footerDiv);
    }
    renderButtonGroupForEdit()  // fmdoel is not used, but kept for compatibility
    {
        if (!this.footerDiv || !this.extraDiv) return;
        const isEditActive = this.modal.querySelector('#modal_edit').classList.contains('btn-active');
        const display = isEditActive ? 'inline-flex' : 'none';
        this.footerDiv.innerHTML = ''; // 清空现有内容
        const buttonContainer = document.createElement('div');
        buttonContainer.style.marginTop = '10px';
        buttonContainer.style.textAlign = 'right';
        buttonContainer.style.display = 'flex';

        // Add row button
        const removeBtn = document.createElement('button');
        removeBtn.id = 'row-remove';
        removeBtn.className = 'el-button el-button--warning el-button--small';
        removeBtn.textContent = '撤销工序';
        removeBtn.dataset.edit = isEditActive;
        removeBtn.style.display = display;

        // Add row button
        const addButton = document.createElement('button');
        addButton.id = 'new-process';
        addButton.textContent = '添加工序';
        addButton.className = 'el-button el-button--primary el-button--small';
        addButton.dataset.edit = isEditActive;
        addButton.style.display = display;

        // Save button
        const saveButton = document.createElement('button');
        saveButton.id = 'table-save'
        saveButton.textContent = '保存';
        saveButton.className = 'el-button el-button--primary el-button--small';
        saveButton.dataset.edit = isEditActive;
        saveButton.style.display = display;
        //saveButton.style.marginLeft = '10px';

        buttonContainer.appendChild(addButton);
        buttonContainer.appendChild(removeBtn);
        buttonContainer.appendChild(saveButton);
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

export function updateSelecterSaveButtonState(container, routeEndPoint) {
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

export class subgongyiGroup{
    constructor(container, params, orderid)
    {
        this.container = container;
        if(params) utils.setDataset(container, params)
        this.params = utils.datasetToObj(container);
        this.OrderId = orderid
        this.url = JSON.parse(this.params?.url ||'{}')
        this.endpoint = this.params?.endpoint || '';
        this.url_params = JSON.parse(this.params?.url_params || '{}');
    }
    render(result)
    {
        BaseRenderer.clearContainer(this.container);
        if(!result) return;
        const subParts = result.map(item => item.parameters)
        this.container.dataset.supParts = JSON.stringify(subParts || [])
        result.forEach((dataItem, index) => {
            dataItem.POrder_id = this.OrderId;
            const subContainer = document.createElement('div');
            subContainer.id = `subgongyi-${index}`;
            subContainer.className = 'el-descriptions el-descriptions--sub';
            const param = {isSubPart : true, title : `${dataItem.FModel} 工艺线路`, 
                body:'table', select:'process'};     
            utils.setDataset(subContainer, param);                
            this.container.appendChild(subContainer);
            new partDescriptions(subContainer, dataItem).renderSubRoute();
        })
    }
}


export class tableRenderer{
    constructor(table, params=null) {
        this.table = table;
        this.params = table? utils.datasetToObj(table) : params;
        this.headers = JSON.parse(this.params?.headers || '[]');
        this.keys = JSON.parse(this.params?.keys || '[]');
        this.hidkeys = JSON.parse(this.params?.hidkeys || '[]');
        this.inputs = JSON.parse(this.params?.inputs || '[]');
        this.uniqKeys = JSON.parse(this.params?.uniqKeys || '[]');
        this.require = JSON.parse(this.params?.require || '[]');        
        this.selects = JSON.parse(this.params?.selects || '[]');
        this.buttons = JSON.parse(this.params?.buttons || '[]');
        this.limit = JSON.parse(this.params?.limit || 0);
        this.page = JSON.parse(this.params?.page || 1);
        this.url = JSON.parse(this.params?.url || '{}')
        this.endpoint = this.params?.endpoint || '';
        this.url_params = JSON.parse(this.params?.url_params || '{}');
        this.data = [];
        this.thead = table?.querySelector('thead');
        this.tbody = table?.querySelector('tbody');
        this.method = 'GET'
        if(this.limit > 0){
            this.url_params.limit = this.limit
            this.url_params.page = this.page
        }
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

    render(result) {
        if(this.method !== 'GET') return this.postRender(result)
        BaseRenderer.clearContainer(this.table);
        this.data = (result && (result.items || result)) || [];  // 默认空数组
        this.total_count = (result && result.count) || 0;        // 默认0
        if(!BaseRenderer.validateParams(this.table, this.data)){
            return;
        } 
        this.createHeader();
        if(this.params['groupkey']) this.createTreeBody(this.params['groupkey']);
        else this.createBody();
        if(this.url_params.limit > 0) this.createPagination(this.total_count, this.page)
    }
    renderError(response) {
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
        input.value = val;
        input.required = request;        
        cell.appendChild(input);
    }

    createSelectForCell(cell, request, key)
    {
        const select = document.createElement('select');  
        select.className = 'optimized-width';
        select.required = request;
        if (Array.isArray(this.selects[key].datas) && this.selects[key].datas.length > 0){
            new selecterRenderer(select).render(this.selects[key].datas)
            select.dataset.datas = JSON.stringify(this.selects[key].datas)
        }    
        select.dataset.url = JSON.stringify(this.selects[key].path || {})
        select.dataset.endpoint = this.selects[key].endpoint||''
        select.dataset.key = this.selects[key].key
        select.dataset.textK = this.selects[key].textK
        cell.appendChild(select)
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
    createCell(val, key) {
        const tdType = this.setTdtype(key, val);
        const cellType = tdType.type;
        const request = tdType.required;
        const cell = document.createElement('td');
        cell.setAttribute('data-key', key.split('.').at(-1));
        if (this.hidkeys.includes(key)) {
            cell.style.display = 'none';
        }
        switch (cellType) {
            case 'input':
                //cell.contentEditable  = true;
                //cell.textContent = val;
                this.createInputForCell(cell, val, request, key);
                break;
            case 'select':
                this.createSelectForCell(cell, request, key);
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
                row.appendChild(this.createCell(val,key));});
        }else{
            this.keys.forEach(key => {row.appendChild(this.createCell('',key));});
        }
        return row;
    }    
    updateRow(row, item){
        if (!row ||!this.table || !this.keys || this.keys.length === 0) return null;
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
    createTreeBody(parentKey='POrder_id') {
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
}
export class descriptionsTable extends tableRenderer {
    constructor(table, params = null) {
        super(table, params); 
        if(this.table){       
            this.table.className = 'el-descriptions__table';
            this.table.style.width = '100%';
            this.table.style.borderCollapse = 'collapse';
            this.id = this.table.id;
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
                selecterRenderer.appendOptionV(selecter, response.routeId)
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
class descriptionsCard extends descriptionsTable {
    constructor(table, params = null) {
        super(table, params);
        if(this.table)
            this.table.className = 'el-descriptions__card';
    }
    render(result) {
        const data = result
        if(!BaseRenderer.validateParams(this.table, data)){
            return;
        } 
        this.table.appendChild(document.createElement('thead'))
        const tbody = document.createElement('tbody')
        for (let i = 0; i < this.headers.length; i += 3) {
            const [labelRow, valueRow] = this.buildCardRows(data[0], i);
            tbody.append(labelRow, valueRow);
        }
        this.table.appendChild(tbody)
    }
    buildCardRows(dataItem, startIdx) {
        const labelRow = document.createElement('tr');
        const valueRow = document.createElement('tr');
        
        for (let j = startIdx; j < startIdx + 3 && j < this.headers.length; j++) {
            labelRow.innerHTML += `
                <td><div><span class="el-descriptions-item__label">
                    ${this.headers[j]}
                </span></div></td>`;
            
            valueRow.innerHTML += `
                <td><div><span class="el-descriptions-item__content">
                    ${this.getValueByPath(dataItem, this.keys[j], '-')}
                </span></div></td>`;
        }
        
        return [labelRow, valueRow];
    }
}
export class selecterRenderer{
    constructor(selecter = null, params = null) {
        this.selecter = selecter
        this.params = selecter ? utils.datasetToObj(this.selecter): params;
        this.default = document.createElement('option');
        this.default.value = "";
        this.default.textContent = this.params?.defaultText || '请选择';
        this.selectedValue = this.selecter?.value || '';
        this.url_params = this.params?.url_params ? JSON.parse(this.params.url_params) : {};
        this.url = JSON.parse(this.params?.url ||'{}')         
        this.endpoint = this.params?.endpoint ||''
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
        const data = result?.items ?? result ?? [];
        this.options = [this.default];
        if (Array.isArray(data) && data.length > 0) {
            data.forEach(item => {
                const option = document.createElement('option');
                option.value = utils.getValueByPath(item, this.params.key );
                option.textContent = this.params.textK? utils.getValueByPath(item, this.params.textK, '' ) 
                : `${this.params.optionText ||''} ${option.value}`;
                this.options.push(option);
            });
            this.selecter.classList.toggle('before', true);
        }
        this.selecter.append(...this.options);
    }
    static appendOptionV(selecter, value) {
        if (!selecter) return false; // 防御性检查
        
        const exists = Array.from(selecter.querySelectorAll('option'))
            .some(option => option.value === value);
        
        if (!exists) {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = `${selecter.dataset.optionText} ${value}`;
            selecter.append(option);
        }
    }
    static change(selecter)
    {
        selecter.classList.toggle('after', true);
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
        data.forEach(step => {
            const div = document.createElement('div');
            div.className = 'step-item';
            div.textContent = step.Name;
            div.dataset.Id = step.Id;
            div.dataset.Name = step.Name;
            div.dataset.EqpName = step.EqpName;
            div.dataset.params = '';
            if(step.FNumber){
                div.dataset.Name = step.EqpName;
                div.dataset.EqpName = step.EqpName;
                div.dataset.params = step.Name;
                div.dataset.FId = step.FId; }
            this.transfer.appendChild(div);
        });
    }
}
export class postTableRenderer extends tableRenderer{
    constructor(table, rowCount = 6){
        super(table);
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
    postRender(result){
        if(!result) return
        alert(result.message || '数据上传成功!');        
        this.createBody(this.rowCount);
        return
    }

}
export class fastFillModelRenderer extends partDescriptions
{
    constructor(container, select_params, table_params)
    {
        super(container)
        this.select_params = select_params || {}
        this.table_parmer = table_params || {}
    }
    render(result) {
        this.container.innerHTML = '';
        this.createLine();
        this.createExtra();
        this.renderHelpNotes();
        this.createHiddenTextarea()
        this.createBody();
        this.createFooter();
        this.renderButtonGroupForEdit();
        this.randerSelecter();
        this.randerTableData(result?.items || result);
        this.textarea.focus()
    }

    createFooter()
    {
        const footerDiv = document.createElement('div');
        footerDiv.className = 'el-descriptions__footer';
        footerDiv.style.marginBottom = '20px';
        footerDiv.style.marginTop = '20px';

        const buttonContainer = document.createElement('div');
        buttonContainer.style.marginTop = '10px';
        buttonContainer.style.textAlign = 'right';
        buttonContainer.style.display = 'flex';
        const removeBtn = document.createElement('button');
        removeBtn.id = 'submit';
        removeBtn.className = 'el-button el-button--warning el-button--small';
        removeBtn.textContent = '确认';
        buttonContainer.appendChild(removeBtn);
        footerDiv.appendChild(buttonContainer);
        this.container.appendChild(footerDiv);
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

    randerSelecter()
    {
        if(this.selecter){
            if (this.select_params && this.select_params.key)
                this.selecter.required = true
            utils.setDataset(this.selecter, this.select_params)
            const selecterRender = new selecterRenderer(this.selecter)
            selecterRender.render(); 
        }  
    }
    randerTableData()
    {
        utils.setDataset(this.tableDiv, this.table_parmer)
        new postTableRenderer(this.tableDiv).initiTable();   
    }
    renderButtonGroupForEdit(){}
}
