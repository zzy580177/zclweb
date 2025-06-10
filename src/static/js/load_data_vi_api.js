

export function loadTreeTableVIAPI(table, apiUrlOverride, groupKey, page = 1, limit = 10) {
    if (!table) return;
    const headers = JSON.parse(table.getAttribute('data-headers'));
    const keys = JSON.parse(table.getAttribute('data-keys'));
    let apiUrl = apiUrlOverride || table.getAttribute('data-api') || '';

    apiUrl = String(apiUrl);
    apiUrl += (apiUrl.includes('?') ? '&' : '?') + `page=${page}&limit=${limit}`;

    // 生成表头
    let thead = table.querySelector('thead');
    if (!thead) {
        thead = document.createElement('thead');
        table.insertBefore(thead, table.firstChild);
    }
    let theadHtml = '<tr>';
    headers.forEach(h => {
        theadHtml += `<td><label>${h}</label></td>`;
    });
    theadHtml += '</tr>';
    thead.innerHTML = theadHtml;

    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            let tableBody = table.querySelector('tbody');
            if (!tableBody) {
                tableBody = document.createElement('tbody');
                table.appendChild(tableBody);
            }
            tableBody.innerHTML = '';

            if (
                data.code !== 200 ||
                data.success !== true ||
                data.message !== "请求成功"
            ) {
                tableBody.innerHTML = `<tr><td colspan="${headers.length}" style="color:red;">${data.message || '接口返回异常'}</td></tr>`;
                return;
            }

            const items = (data.data && data.data.items) ? data.data.items : [];
            if (items.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="${headers.length}" style="color:#888;">暂无数据</td></tr>`;
                return;
            }

            // 按 groupKey 分组
            const groups = {};
            items.forEach(item => {
                const groupVal = getValueByPath(item, groupKey);
                if (!groups[groupVal]) groups[groupVal] = [];
                groups[groupVal].push(item);
            });

            Object.keys(groups).forEach((groupVal, idx) => {
                // 父行（POrder分组行）
                const groupId = `tree-group-${idx}`;
                const parentTr = document.createElement('tr');
                parentTr.className = 'tree-parent';
                parentTr.style.cursor = 'pointer';
                parentTr.innerHTML = `<td colspan="${headers.length}" style="background:#f6f6f6;">
                    <span class="tree-toggle" data-group="${groupId}" style="font-weight:bold;">&#9654; ${groupVal}</span>
                </td>`;
                tableBody.appendChild(parentTr);

                // 子项
                groups[groupVal].forEach(item => {
                    const tr = document.createElement('tr');
                    tr.className = `tree-child ${groupId}`;
                    tr.style.display = 'none';
                    tr.innerHTML = keys.map(k => `<td>${getValueByPath(item, k)}</td>`).join('');
                    tableBody.appendChild(tr);
                });
            });

            // 展开/收起事件
            tableBody.querySelectorAll('.tree-toggle').forEach(toggle => {
                toggle.onclick = function() {
                    const groupId = this.getAttribute('data-group');
                    const children = tableBody.querySelectorAll(`tr.${groupId}`);
                    const isOpen = this.textContent.startsWith('▼');
                    children.forEach(tr => tr.style.display = isOpen ? 'none' : '');
                    this.innerHTML = (isOpen ? '&#9654;' : '&#9660;') + ' ' + this.textContent.replace(/^(\u25BC|\u25B6)\s*/, '');
                };
            });

            // 分页控件
            renderPagination(table, data.data.count || 0, page, limit, apiUrlOverride);
        })
        .catch(err => {
            let tableBody = table.querySelector('tbody');
            if (!tableBody) {
                tableBody = document.createElement('tbody');
                table.appendChild(tableBody);
            }
            tableBody.innerHTML = `<tr><td colspan="${headers.length}" style="color:red;">加载失败</td></tr>`;
        });
}

// 复用 getValueByPath 和 renderPagination

export function loadTableVIAPI(table, apiUrlOverride, page = 1, limit = 10) {
    if (!table) return;
    const headers = JSON.parse(table.getAttribute('data-headers'));
    const keys = JSON.parse(table.getAttribute('data-keys'));
    let apiUrl = apiUrlOverride || table.getAttribute('data-api') || '';

    apiUrl = String(apiUrl); // 保证一定是字符串
    apiUrl += (apiUrl.includes('?') ? '&' : '?') + `page=${page}&limit=${limit}`;

    // 先生成表头
    let thead = table.querySelector('thead');
    if (!thead) {
        thead = document.createElement('thead');
        table.insertBefore(thead, table.firstChild);
    }
    let theadHtml = '<tr>';
    headers.forEach(h => {
        theadHtml += `<td><label>${h}</label></td>`;
    });
    theadHtml += '</tr>';
    thead.innerHTML = theadHtml;

    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            let tableBody = table.querySelector('tbody');
            if (!tableBody) {
                tableBody = document.createElement('tbody');
                table.appendChild(tableBody);
            }
            tableBody.innerHTML = '';

            if (
                data.code !== 200 ||
                data.success !== true ||
                data.message !== "请求成功"
            ) {
                tableBody.innerHTML = `<tr><td colspan="${headers.length}" style="color:red;">${data.message || '接口返回异常'}</td></tr>`;
                return;
            }

            const items = (data.data && data.data.items) ? data.data.items : [];
            if (items.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="${headers.length}" style="color:#888;">暂无数据</td></tr>`;
                return;
            }
            
            items.forEach(item => {
                const tr = document.createElement('tr');
                tr.innerHTML = keys.map(k => `<td>${getValueByPath(item, k)}</td>`).join('');
                tableBody.appendChild(tr);
            });

            // 分页控件
            renderPagination(table, data.data.count || 0, page, limit, apiUrlOverride);
        })
        .catch(err => {
            const tableBody = table.querySelector('tbody');
            if (tableBody) {
                tableBody.innerHTML = `<tr><td colspan="${headers.length}" style="color:red;">加载失败</td></tr>`;
            }
        });
}
// 辅助函数：支持 'Part.FNumber' 取值
function getValueByPath(obj, path) {
    return path.split('.').reduce((acc, key) => (acc && acc[key] !== undefined) ? acc[key] : '', obj);
}
// 渲染分页控件
function renderPagination(table, total, page, limit, apiUrlOverride) {
    let pager = table.nextElementSibling;
    if (!pager || !pager.classList.contains('table-pager')) {
        pager = document.createElement('div');
        pager.className = 'table-pager';
        pager.style = 'margin:10px 0;text-align:center;';
        table.parentNode.insertBefore(pager, table.nextSibling);
    }
    const totalPages = Math.max(1, Math.ceil(total / limit));
    page = Math.max(1, Math.min(page, totalPages));

    let html = `共 ${total} 条 `;

    // 上一页
    if (page > 1) {
        html += `<a href="#" data-page="${page - 1}" class="pager-btn">&lt;</a>`;
    } else {
        html += `<span class="pager-btn pager-disabled">&lt;</span>`;
    }

    // 数字页码（最多显示7个，含省略号）
    let start = Math.max(1, page - 2);
    let end = Math.min(totalPages, page + 2);
    if (page <= 3) end = Math.min(5, totalPages);
    if (page >= totalPages - 2) start = Math.max(1, totalPages - 4);

    if (start > 1) {
        html += `<a href="#" data-page="1" class="pager-btn">1</a>`;
        if (start > 2) html += `<span class="pager-ellipsis">...</span>`;
    }
    for (let i = start; i <= end; i++) {
        if (i === page) {
            html += `<b class="pager-btn pager-current">${i}</b>`;
        } else {
            html += `<a href="#" data-page="${i}" class="pager-btn">${i}</a>`;
        }
    }
    if (end < totalPages) {
        if (end < totalPages - 1) html += `<span class="pager-ellipsis">...</span>`;
        html += `<a href="#" data-page="${totalPages}" class="pager-btn">${totalPages}</a>`;
    }

    // 下一页
    if (page < totalPages) {
        html += `<a href="#" data-page="${page + 1}" class="pager-btn">&gt;</a>`;
    } else {
        html += `<span class="pager-btn pager-disabled">&gt;</span>`;
    }

    // 跳转输入框
    html += `&nbsp;前往 <input type="number" min="1" max="${totalPages}" value="${page}" class="pager-input" style="width:40px;text-align:center;"> 页`;

    pager.innerHTML = html;

    // 绑定点击事件
    pager.querySelectorAll('a[data-page]').forEach(a => {
        a.onclick = function(e) {
            e.preventDefault();
            loadTableVIAPI(table, apiUrlOverride, parseInt(a.dataset.page), limit);
        };
    });

    // 跳转输入框事件
    const input = pager.querySelector('.pager-input');
    if (input) {
        input.onkeydown = function(e) {
            if (e.key === 'Enter') {
                let val = parseInt(input.value);
                if (!isNaN(val) && val >= 1 && val <= totalPages) {
                    loadTableVIAPI(table, apiUrlOverride, val, limit);
                }
            }
        };
    }
}

/**
 * 重构版：将数据填充到已存在的 el-descriptions 结构中
 * @param {string} title - 标题
 * @param {object} data - API返回的对象
 * @param {Array} fields - 需要展示的字段及标签 [{label: '用户名', key: 'username'}, ...]
 * @param {string} containerId - 容器ID（el-descriptions 外层div的id）
 */
function renderDescriptions(title, data, fields, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    // 找到 el-descriptions 结构
    const desc = container.querySelector('.el-descriptions');
    if (!desc) return;

    if (desc) desc.classList.remove('el-descriptions--border', 'is-bordered');
    // 填充标题
    const titleDiv = desc.querySelector('.el-descriptions__title');
    if (titleDiv) titleDiv.textContent = title || '';

    // 填充内容
    const tbody = desc.querySelector('.el-descriptions__table > tbody');
    if (!tbody) return;
    tbody.innerHTML = ''; // 清空原内容

    for (let i = 0; i < fields.length; i += 3) {
        const labeltr = document.createElement('tr');
        labeltr.className = 'el-descriptions-row';
        const contentltr = document.createElement('tr');
        labeltr.className = 'el-descriptions-row';
        for (let j = i; j < i + 3 && j < fields.length; j++) {
            const field = fields[j];
            const td1 = document.createElement('td');
            td1.colSpan = 1;
            td1.className = 'el-descriptions-item el-descriptions-item__cell';
            td1.innerHTML = `
                <div class="el-descriptions-item__container">
                    <span class="el-descriptions-item__label">${field.label}</span>
                </div>
            `;
            const td2 = document.createElement('td');
            td2.colSpan = 1;
            td2.className = 'el-descriptions-item el-descriptions-item__cell';
            td2.innerHTML = `
                <div class="el-descriptions-item__container">
                    <span class="el-descriptions-item__content">${getValueByPath(data, field.key) ?? ''}</span>
                </div>
            `;
            labeltr.appendChild(td1);
            contentltr.appendChild(td2);          
        }
        tbody.appendChild(labeltr);
        tbody.appendChild(contentltr);
    }
}

function createDescriptionsSkeleton(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // 清空容器
    while (container.firstChild) container.removeChild(container.firstChild);

    // el-descriptions
    const desc = document.createElement('div');
    desc.className = 'el-descriptions';

    // header
    const header = document.createElement('div');
    header.className = 'el-descriptions__header';

    const titleDiv = document.createElement('div');
    titleDiv.className = 'el-descriptions__title';
    header.appendChild(titleDiv);

    const extraDiv = document.createElement('div');
    extraDiv.className = 'el-descriptions__extra';
    header.appendChild(extraDiv);

    desc.appendChild(header);

    // 蓝色分割线
    const line = document.createElement('div');
    line.style.height = '1px';
    line.style.background = '#2f7deb';
    line.style.borderRadius = '1px';
    line.style.margin = '8px 0';
    desc.appendChild(line);

    
    // body
    const body = document.createElement('div');
    body.className = 'el-descriptions__body';

    const table = document.createElement('table');
    table.className = 'el-descriptions__table';
    table.style.width = '100%';
    table.style.borderCollapse = 'collapse';

    const tbody = document.createElement('tbody');
    table.appendChild(tbody);

    body.appendChild(table);
    desc.appendChild(body);
    container.appendChild(desc);
}

function createDescriptionsAndRenderData(containerId, title, data, fields) 
{
    createDescriptionsSkeleton(containerId);
    renderDescriptions(title, data, fields, containerId);
}

let FNumber = '';
    // 示例：调用API并渲染
export function loadAndRenderDescriptionsPart1(url) {
        fetch(url)
            .then(res => res.json())
            .then(data => {
                // 根据实际API返回结构调整字段
                const parts_fields = [
                    { label: '组别', key: 'Part.FGroup.FName' },
                    { label: '物料编码', key: 'Part.FNumber' },
                    { label: '物料名称', key: 'Part.FName' },
                    { label: '规格型号', key: 'Part.FModel' },
                    { label: '生产单位', key: 'Part.FUnit.Name' },                                       
                    { label: '生产数量', key: 'Quantity' },                    
                    { label: '零件当前状态', key: 'Status' },                 
                    { label: '交付截至', key: 'DeadLine' }
                    // ...可扩展更多字段
                ];
                const order_fields = [
                    { label: '订单', key: 'OrderId' },
                    { label: '产品信息', key: 'Product_id' },
                    { label: '批次号', key: 'LotId' },                    
                    { label: '订单状态', key: 'Status' },                 
                    { label: '截至日期', key: 'DeadLine' }
                    // ...可扩展更多字段
                ];
                FNumber = data.data.items[0].Part.FNumber;
                const part = data.data.items[0].Part
                const partName = (part.FName === 'NULL' ) ? '' : part.FName|| '';
                const partModel = (part.FModel === 'NULL' ) ? '' : part.FModel|| '';
                const titleTextDiv = document.querySelector('.title-text');
                if (titleTextDiv) {
                    titleTextDiv.textContent = `${partModel}  ${partName}`;
                    titleTextDiv.setAttribute('title', `${partModel}  ${partName}`);
                }
                createDescriptionsAndRenderData('descriptions-order', '订单信息', data.data.items[0].POrder, order_fields);
                createDescriptionsAndRenderData('descriptions-wuliao', '零件信息', data.data.items[0], parts_fields);

            });
}
    let currentIndex = 1; // Start index counter
    function reRenderTable(containerId, fields) {
        const container = document.getElementById(containerId);
        if (!container) return null;
        
        // Use querySelector to get a single element instead of NodeList
        const tableDiv = container.querySelector('.el-descriptions__table');
        if (!tableDiv) return;
        
        // 重置表格样式
        tableDiv.className = 'el-table el-table--fit el-table--scrollable-x el-table--scrollable-y';
        
        // 清空现有内容
        tableDiv.innerHTML = '';
        currentIndex = 1
        // 创建表格结构
        const table = document.createElement('table');
        const thead = document.createElement('thead');
        const tbody = document.createElement('tbody');
        
        // 创建表头
        const headerRow = document.createElement('tr');
        fields.forEach(field => {
            const th = document.createElement('th');
            th.textContent = field.label;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        
        // 组装表格
        table.appendChild(thead);
        table.appendChild(tbody);
        tableDiv.appendChild(table);

        // After the table is created and appended to tableDiv
        const buttonContainer = document.createElement('div');
        buttonContainer.style.marginTop = '10px';
        buttonContainer.style.textAlign = 'right';

        // Add row button
        const removeBtn = document.createElement('button');
        removeBtn.className = 'el-button el-button--warning el-button--small';
        removeBtn.textContent = '撤销工序';
        removeBtn.onclick = function() {
            if (tbody.rows.length > 1) {
                const row = tbody.rows[tbody.rows.length - 1];
                row.remove();
                currentIndex--;
            }
        };

        // Add row button
        const addButton = document.createElement('button');
        addButton.textContent = '新增工序';
        addButton.className = 'el-button el-button--primary el-button--small';
        addButton.onclick = function() {
            addTableRow(tbody, fields);
            currentIndex++
        };

        // Save button
        const saveButton = document.createElement('button');
        saveButton.textContent = '保存';
        saveButton.className = 'el-button el-button--primary el-button--small';
        saveButton.style.marginLeft = '10px';
        saveButton.onclick = function() {
            // Save functionality to be implemented
            alert('保存功能待实现');
        };
        buttonContainer.appendChild(removeBtn);
        buttonContainer.appendChild(addButton);
        buttonContainer.appendChild(saveButton);
        tableDiv.appendChild(buttonContainer);

        // 添加默认行
        addTableRow(tbody, fields); 
        currentIndex++;

    }

    function addTableRow(tbody, fields) {
        const row = document.createElement('tr');
            
        fields.forEach(col => {
            const cell = document.createElement('td');
            const span = document.createElement('span');
            span.name = col.key.split('.').pop();
            if (col.key === 'Index') {
                span.textContent = currentIndex;
            }
            if(col.type !== '') {
                cell.appendChild(span);
                row.appendChild(cell);
            }
        });

        // 添加操作按钮单元格
        const actionCell = document.createElement('td');

        const editBtn = document.createElement('button');
        editBtn.className = 'el-button el-button--primary el-button--small';
        editBtn.textContent = '编辑';
        editBtn.onclick = function() {
            // 编辑功能待实现
            alert('编辑功能待实现'+FNumber+ String(currentIndex));
        };

        actionCell.appendChild(editBtn);
        row.appendChild(actionCell);

        tbody.appendChild(row);
    }


    /**
     * 重构版：将数据填充到已存在的 el-descriptions 结构中
     * @param {string} title - 标题
     * @param {object} data - API返回的对象
     * @param {Array} fields - 需要展示的字段及标签 [{label: '用户名', key: 'username'}, ...]
     * @param {string} containerId - 容器ID（el-descriptions 外层div的id）
     */
    function renderReRenderTable(title, data, fields, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        // 找到 el-descriptions 结构
        const desc = container.querySelector('.el-descriptions');
        if (!desc) return;

        // 填充标题
        const titleDiv = desc.querySelector('.el-descriptions__title');
        if (titleDiv) titleDiv.textContent = title || '';

        // 填充内容
        const tbody = desc.querySelector('.el-table > tbody');
        if (!tbody) return;
        tbody.innerHTML = ''; // 清空原内容

        for (let i = 0; i < fields.length; i += 3) {
            const labeltr = document.createElement('tr');
            labeltr.className = 'el-descriptions-row';
            const contentltr = document.createElement('tr');
            labeltr.className = 'el-descriptions-row';
            for (let j = i; j < i + 3 && j < fields.length; j++) {
                const field = fields[j];
                const td1 = document.createElement('td');
                td1.colSpan = 1;
                td1.className = 'el-descriptions-item el-descriptions-item__cell';
                td1.innerHTML = `
                    <div class="el-descriptions-item__container">
                        <span class="el-descriptions-item__label">${field.label}</span>
                    </div>
                `;
                const td2 = document.createElement('td');
                td2.colSpan = 1;
                td2.className = 'el-descriptions-item el-descriptions-item__cell';
                td2.innerHTML = `
                    <div class="el-descriptions-item__container">
                        <span class="el-descriptions-item__content">${getValueByPath(data, field.key) ?? ''}</span>
                    </div>
                `;
                labeltr.appendChild(td1);
                contentltr.appendChild(td2);          
            }
            tbody.appendChild(labeltr);
            tbody.appendChild(contentltr);
        }
    }

export function loadAndRenderDescriptionsPart2(url, stepGroup) {
        fetch(url)
            .then(res => res.json())
            .then(data => {
                // 根据实际API返回结构调整字段
                const parm_fields = [
                    { label: '材料', key: 'Stuff' },
                    { label: '加工尺寸', key: 'Size' },
                    { label: '毛料尺寸', key: 'Cost' },                 
                    { label: '镀层要求', key: 'Surface' },                 
                    { label: '备注', key: 'Description' },
                    // ...可扩展更多字段
                ];
                const step_fields = [                    
                    { label: '工序序号', key: 'Index', type: 'number', required: true},
                    { label: '设备', key: 'Group', type: 'select', required: true,  options: stepGroup},
                    { label: '工序列表', key: 'Steps', type: 'text', required: true},
                    { label: '加工参数', key: 'parmeters', type: 'text', required: true},
                    { label: '备注', key: 'Description', type: 'text', required: true},
                    { label: '操作', key: '', type: '', enable: true},
                    // ...可扩展更多字段
                ];

                createDescriptionsAndRenderData('descriptions-chanshu', '规格参数', data.data.items[0], parm_fields);                
                createDescriptionsSkeleton('descriptions-gongyi');
                reRenderTable('descriptions-gongyi', step_fields)
                renderReRenderTable('工艺线路', [], step_fields, 'descriptions-gongyi');

            });
}
