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
    let theadHtml = '<tr> <div style = "font-weight: bold">';
    headers.forEach(h => {
        theadHtml += `<td><label>${h}</label></td>`;
    });
    theadHtml += '</div></tr>';
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
            }
        }
    }

let currentIndex = 1; 

export function renderDescriptionsFrame(containerId, title, tableHeaders, dataKeys, url) {
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
        titleDiv.textContent = title || '';
        header.appendChild(titleDiv);
        desc.appendChild(header);

        // 蓝色分割线
        const line = document.createElement('div');
        line.style.height = '1px';
        line.style.background = '#2f7deb';
        line.style.borderRadius = '1px';
        line.style.margin = '8px 0';
        desc.appendChild(line);

        
        const extraDiv = document.createElement('div');
        extraDiv.className = 'el-descriptions__extra';
        extraDiv.style.marginBottom = '20px';
        extraDiv.style.marginTop = '20px';
        desc.appendChild(extraDiv);
        
        // body
        const body = document.createElement('div');
        body.className = 'el-descriptions__body';
        const table = document.createElement('table');
        table.dataset.headers = JSON.stringify(tableHeaders);
        table.dataset.keys = JSON.stringify(dataKeys);
        table.dataset.api = url;

        table.className = 'el-descriptions__table';
        table.style.width = '100%';
        table.style.borderCollapse = 'collapse';

        const tbody = document.createElement('tbody');
        table.appendChild(tbody);
        body.appendChild(table);
        desc.appendChild(body);

        const footerDiv = document.createElement('div');
        footerDiv.className = 'el-descriptions__footer';
        footerDiv.style.marginBottom = '20px';
        footerDiv.style.marginTop = '20px';
        desc.appendChild(footerDiv);

        container.appendChild(desc);
    }

export function loadDetTableVIAPI(table, apiUrlOverride, isClean = true) {
    if (!table) return Promise.resolve([]);
    const headers = JSON.parse(table.getAttribute('data-headers'));
    const keys = JSON.parse(table.getAttribute('data-keys'));
    let apiUrl = apiUrlOverride || table.getAttribute('data-api') || '';

    apiUrl = String(apiUrl); 

    // 生成表头
    let thead = table.querySelector('thead');
    if (!thead) {
        thead = document.createElement('thead');
        table.insertBefore(thead, table.firstChild);
    }

    return fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            let tableBody = table.querySelector('tbody');
            if (!tableBody) {
                tableBody = document.createElement('tbody');
                table.appendChild(tableBody);
            }
            if(isClean) tableBody.innerHTML = '';

            if (data.code !== 200 || data.success !== true || data.message !== "请求成功") {
                tableBody.innerHTML = `<tr><td colspan="${headers.length}" style="color:red;">${data.message || '接口返回异常'}</td></tr>`;
                return Promise.resolve([]);
            }

            const items = (data.data && data.data.items) ? data.data.items : [];
            if (items.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="${headers.length}" style="color:#888;">暂无数据</td></tr>`;
                return Promise.resolve([]);
            }
            const sub_parts = (items[0].Part && items[0].Part.sub_parts) ? items[0].Part.sub_parts : [];
            // 原有渲染逻辑
            for (let i = 0; i < headers.length; i += 3) {
                const tr1 = document.createElement('tr');
                const tr2 = document.createElement('tr');
                let row1 = ``;
                let row2 = ``;
                for (let j = i; j < i + 3 && j < headers.length; j++) {
                    row1 = `${row1} <td> <div ><span class="el-descriptions-item__label">${headers[j]}</span></div></td>`;
                    row2 = `${row2} <td> <div ><span class="el-descriptions-item__content"> ${getValueByPath(items[0], keys[j])}</span></div></td>`;
                }
                tr1.innerHTML = row1;
                tr2.innerHTML = row2;
                tableBody.appendChild(tr1);
                tableBody.appendChild(tr2);
            }
            return Promise.resolve(sub_parts);
        })
        .catch(err => {
            console.error('加载失败:', err);
            const tableBody = table.querySelector('tbody');
            if (tableBody) {
                tableBody.innerHTML = `<tr><td colspan="${headers.length}" style="color:red;">加载失败</td></tr>`;
            }
            return Promise.resolve([]);
        });
}

export function addDesignProcessButtonForGongyi(FNumber) {
        const container = document.getElementById('descriptions-gongyi');
        const div = container.querySelector('.el-descriptions .el-descriptions__footer');
        if (!div) return;
        currentIndex = 1; // 重置当前索引

        // After the table is created and appended to tableDiv
        const buttonContainer = document.createElement('div');
        buttonContainer.style.marginTop = '10px';
        buttonContainer.style.textAlign = 'right';
        buttonContainer.style.display = 'flex';

        // Add row button
        const removeBtn = document.createElement('button');
        removeBtn.className = 'el-button el-button--warning el-button--small';
        removeBtn.textContent = '撤销工序';
        removeBtn.onclick = function() {
            const tbody = container.querySelector('.el-descriptions .el-descriptions__table tbody');
            if (tbody.rows.length > 0) {
                const row = tbody.rows[tbody.rows.length - 1];
                row.remove();
                currentIndex--;
            }
        };

        // Add row button
        const addButton = document.createElement('button');
        addButton.textContent = '添加工序';
        addButton.className = 'el-button el-button--primary el-button--small';
        addButton.onclick = function() {
            const tbody = container.querySelector('.el-descriptions .el-descriptions__table tbody');
            currentIndex = tbody.rows.length + 1; // 更新当前索引
            const overlaymodal = document.getElementById('process-design-modal-overlay');
            const modal = document.getElementById('process-design-modal');
            overlaymodal.style.display = 'block';
            modal.style.display = 'block';
            
        };

        // Save button
        const saveButton = document.createElement('button');
        saveButton.textContent = '保存';
        saveButton.className = 'el-button el-button--primary el-button--small';
        saveButton.style.marginLeft = '10px';
        saveButton.onclick = function() {
            saveDesignedProcess(FNumber);
        };
        buttonContainer.appendChild(addButton);
        buttonContainer.appendChild(removeBtn);
        buttonContainer.appendChild(saveButton);
        div.appendChild(buttonContainer);
    }

    
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

    function saveDesignedProcess(FNumber) {
        const container = document.getElementById('descriptions-gongyi');
        const tbody = container.querySelector('.el-descriptions .el-descriptions__table tbody');
        const rows = tbody.querySelectorAll('tr');
        
        // 提取表格数据
        const processData = [];
        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            const rowData = {
                seqNum: cells[0].textContent.trim(),
                eqpName: cells[1].textContent.trim(),
                stepList: cells[2].textContent.trim(),
                params: cells[3].textContent.trim(),
                description: cells[4].textContent.trim(),
            };
            processData.push(rowData);
        });
        const spanEls = document.querySelectorAll('.el-descriptions-item__content');
        const order = spanEls[0].textContent.trim();  
        const number = spanEls[6].textContent.trim();  
        const selectRoute = document.querySelector('#process-select').value.trim();

        fetch('saveProcess/', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({steps: processData, order: order, number: number, route: selectRoute})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message || '工艺数据已保存！');
                // 可选：保存成功后刷新页面或关闭弹窗
                refreshProcessRouteSelect(FNumber, data.route_id);
            } else {
                alert(data.message || '保存失败，请检查数据！');
            }
        })
        .catch(error => {
            console.error('保存失败:', error);
            alert('保存失败，请重试！');
        });
    }

export function addSelectProcessButtonForGongyi(FNumber) {
        const container = document.getElementById('descriptions-gongyi');
        const div = container.querySelector('.el-descriptions .el-descriptions__extra');
        if (!div) return;
        div.style.display = 'flex';
        div.style.gap = '10px';

        // 创建工序选择器
        const select = document.createElement('select');
        select.className = 'el-select__inner';
        select.id = 'process-select';

        // 先添加默认选项
        refreshProcessRouteSelect(FNumber, null, select);

        // select变更时自动fetch并渲染
        select.addEventListener('change', function() {
            const routeId = select.value;
            if (!routeId) return;
            fetchAndRenderProcessRouteToTable(routeId, container);
        });

        // 创建确认按钮
        const button = document.createElement('button');
        button.className = 'el-button el-button--primary  el-button--small';
        button.textContent = '确认选择';
        button.addEventListener('click', () => {
            alert(`已选择工序: ${select.value}`);
            // 这里添加实际业务逻辑
        });

        // 组装元素
        div.appendChild(select);
        div.appendChild(button);
    }

    function refreshProcessRouteSelect(FNumber, routeId = null, input_select = null) {
        const select = document.getElementById('process-select') || input_select;
        if (!select) return;
        const url = `/api/pmcui/process_route/process_route?FNumber=${FNumber}`;
        fetchDataViApiUrl(url).then(routes => {
            // 清空原有选项
            select.innerHTML = '';
            // 添加默认选项
            const defaultOption = document.createElement('option');
            defaultOption.value = "";
            defaultOption.textContent = "请选择历史工艺线路设计";
            select.appendChild(defaultOption);
            // 添加新选项
            routes.forEach(route => {
                const option = document.createElement('option');
                option.value = route.Id;
                option.textContent = route.Product_id || `工艺路线${route.Id}`;
                select.appendChild(option);
            });
        });
        // 设置选中为刚保存的 routeId
        if (routeId)
        {
            select.value = routeId;                
            select.textContent = `工艺路线${routeId}`;
            select.dispatchEvent(new Event('change'));
        }
    }

    function fetchDataViApiUrl(url) {
        return fetch(url)
            .then(res => res.json())
            .then(data => {
                if (!data.success) {
                    console.error('API请求失败:', data.message || '未知错误');
                    return [];
                }
                // 兼容后端返回结构
                if (Array.isArray(data)) return data;
                if (data.items) return data.items;
                if (data.data && data.data.items) return data.data.items;
                if (data.data && typeof data.data === 'object') return data.data;
                return [];
            })
            .catch(() => []);
    }

    // 渲染工艺路线到表格
    function fetchAndRenderProcessRouteToTable(routeId, container) {
        const url = `/api/pmcui/process_route/process_route_steps/${routeId}`;
        fetchDataViApiUrl(url).then(routeData => {
            // 假设 routeData.main_steps 是步骤数组
            const table = container.querySelector('.el-descriptions__table');
            if (!table) return;
            const tbody = table.querySelector('tbody');
            if (!tbody) return;
            tbody.innerHTML = ''; // 清空原有内容

            if (!routeData.main_steps || !Array.isArray(routeData.main_steps) || routeData.main_steps.length === 0) {
                const tr = document.createElement('tr');
                tr.innerHTML = `<td colspan="5" style="color:#888;">该工艺路线无步骤</td>`;
                tbody.appendChild(tr);
                return;
            }

            routeData.main_steps.forEach((step, idx) => {
                // 处理 Steps 多行
                const steps = Array.isArray(step.Steps) ? step.Steps : [];
                // 拼接所有 step.Name
                const stepNames = steps.map(s => s.step && s.step.Name ? s.step.Name : '').join('; <br>');
                // 拼接所有 step.Name: parameters
                const stepParams = steps.map(s => {
                    const name = s.step && s.step.Name ? s.step.Name : '';
                    const param = s.parameters != "" ? s.parameters : 'null';
                    return `${name}${param !== '' ? ':' + param : ''}`;
                }).join('; <br>');

                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${step.SeqNum || ''}</td>
                    <td>${steps[0] && steps[0].step && steps[0].step.EqpType && steps[0].step.EqpType.Name ? steps[0].step.EqpType.Name : ''}</td>
                    <td>${stepNames}</td>
                    <td>${stepParams}</td>
                    <td>${step.Description || ''}</td>
                `;
                tbody.appendChild(tr);
            });
        })
    }

    // 加载工序组数据
export function loadStepsByGroup(containerID, url) {
    if(!containerID || !document.getElementById(containerID)) {
        console.error('无效的容器ID');
        return;
    }
    
    const groupId = document.getElementById(containerID).value;
    const selectedEl = document.getElementById('selected-steps');
    const availableEl = document.getElementById('available-steps');
    const paramTableEl = document.querySelector('#param-table tbody');
    const remarkEl = document.getElementById('remark');
    
    // 清空已选工序
    selectedEl && (selectedEl.innerHTML = '');
    paramTableEl && (paramTableEl.innerHTML = '');
    remarkEl && (remarkEl.value = '');
    if(!groupId) {
        availableEl && (availableEl.innerHTML = '');
        return;
    }
    fetch(url)
        .then(res => {
            if(!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
            return res.json();
        })
        .then(data => {
            if(data?.data?.items) {
                renderAvailableSteps(data.data.items);
            } else {
                console.warn('返回数据格式不符合预期');
            }
        })
        .catch(error => {
            console.error('请求失败:', error);
            availableEl && (availableEl.innerHTML = '加载失败');
        });
    }


    // 渲染可选工序
    function renderAvailableSteps(data) {
        const container = document.getElementById('available-steps');
        container.innerHTML = '';
        
        data.forEach(step => {
            const div = document.createElement('div');
            div.className = 'step-item';
            div.textContent = step.Name;
            div.dataset.id = step.Id;
            div.onclick = function() {
                addSelectedStep(step);
            };
            container.appendChild(div);
        });
    }

    // 添加已选工序
    function addSelectedStep(step) {
        const container = document.getElementById('selected-steps');
        const div = document.createElement('div');
        div.className = 'step-item';
        div.textContent = step.Name;
        // 生成唯一标识
        const uuid = Date.now().toString() + Math.random().toString(36).slice(2);
        div.dataset.uuid = uuid;
        div.dataset.stepId = step.Id; // 如需追踪原始step.Id
        div.onclick = function() {
            container.removeChild(div); // 直接移除当前点击的div
            removeParamTable(uuid);     // 用uuid移除参数表
        };
        container.appendChild(div);
        renderParamTable(step, uuid);   // 传uuid给参数表
    }

    // 渲染参数表格
    function renderParamTable(step, uuid) {
        const table = document.querySelector('#param-table tbody');
        const newRow = table.insertRow();
        newRow.dataset.uuid = uuid;
        newRow.insertCell(0).textContent = step.Name;
        newRow.insertCell(1).innerHTML = `<input type="text" class="el-input__inner" data-step="${step.Id}">`;
    }

    // 移除参数表格
    function removeParamTable(uuid) {
        const tbody = document.querySelector('#param-table tbody');
        if (!tbody) return;
        const row = tbody.querySelector(`tr[data-uuid="${uuid}"]`);
        if (row) tbody.removeChild(row);
    }
    
export function LoadDateFromStepDesign()
    {
        const table = document.querySelector('#param-table tbody');
        if (!table) return null;
        
        const paramsList = [];
        const stepsList = [];
        const rows = table.querySelectorAll('tr');
        
        rows.forEach(row => {
            const stepId = row.dataset.stepId;
            const stepName = row.cells[0].textContent;
            const inputValue = row.cells[1].querySelector('input').value ||"null";
            paramsList.push(stepName + ":" + inputValue);
            stepsList.push(stepName)
        });

        const targetTbody = document.querySelector('#descriptions-gongyi table tbody');;
        const fields = ['Index','Group','Steps','parmeters','Description'];
        
        const row = document.createElement('tr');
        fields.forEach(col => {
            const cell = document.createElement('td');
            const span = document.createElement('span');
            span.name = col;
            if (col === 'Index') {
                span.textContent = currentIndex;
                currentIndex ++;
            }else if (col === 'Steps') {
                span.textContent = stepsList.join('; ');
            }else if (col === 'parmeters') {
                span.textContent = paramsList.join('; ');
            }else if (col === 'Group') {
                span.textContent = document.getElementById('select-step-group').value || '';
            }else if (col === 'Description') {
                span.textContent = document.getElementById('remark').value || 'null';
            }
            cell.appendChild(span);
            row.appendChild(cell);
        });
        targetTbody.appendChild(row);

    }
export function renderOrderPartsParmTable() {
        const subPartsH = ['子件编码', '子件名称', '规格型号', '生产单位'];        
        const subPartKeys = ['FNumber','FName','FModel','unit'];
        const orderTable = container.querySelector('#descriptions-order .el-descriptions .el-descriptions__table');
        loadDetTableVIAPI(orderTable);
        
        const wuliaoTable = container.querySelector('#descriptions-wuliao .el-descriptions .el-descriptions__table');
        loadDetTableVIAPI(wuliaoTable)
            .then(subParts => {
                if (subParts && subParts.length > 0) {
                    renderDescriptionsFrame('descriptions-subparts', '中间件信息', subPartsH, subPartKeys, '');
                    const subPartsTable = container.querySelector('#descriptions-subparts .el-descriptions .el-descriptions__table');
                    loadDetTableVIData(subPartsTable, {sub_parts: subParts});
                }
            });

        const pamarTable = container.querySelector('#descriptions-chanshu .el-descriptions .el-descriptions__table');
        loadDetTableVIAPI(pamarTable);    
        const processTable = container.querySelector('#descriptions-gongyi .el-descriptions .el-descriptions__table');        
        loadTableVIAPI(processTable);
        const cncprocessTable = container.querySelector('#descriptions-cnc-gongyi .el-descriptions .el-descriptions__table');        
        loadTableVIAPI(cncprocessTable);
    }

    function loadDetTableVIData(table, data, isClean = true) {
        if (!table) return Promise.resolve([]);
        const headers = JSON.parse(table.getAttribute('data-headers'));
        const keys = JSON.parse(table.getAttribute('data-keys'));


        let thead = table.querySelector('thead');
        if (!thead) {
            thead = document.createElement('thead');
            table.insertBefore(thead, table.firstChild);
        }
        let theadHtml = '<tr> <div style = "font-weight: bold">';
        headers.forEach(h => {
            theadHtml += `<td><label><span class="el-descriptions-item__label">${h}</span></label></td>`;
        });
        theadHtml += '</div></tr>';
        thead.innerHTML = theadHtml;

        let tableBody = table.querySelector('tbody');
        if (!tableBody) {
            tableBody = document.createElement('tbody');
            table.appendChild(tableBody);
        }
        tableBody.innerHTML = '';

        data.sub_parts.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = keys.map(k => `<td>${getValueByPath(item, k)}</td>`).join('');
            tableBody.appendChild(tr);
        });
    }
