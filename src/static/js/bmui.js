const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

// 显示加载中动画
export function showLoading() {
    const loadingOverlay = document.createElement("div");
    loadingOverlay.id = "loading-overlay";
    loadingOverlay.style.position = "fixed";
    loadingOverlay.style.top = "0";
    loadingOverlay.style.left = "0";
    loadingOverlay.style.width = "100%";
    loadingOverlay.style.height = "100%";
    loadingOverlay.style.backgroundColor = "rgba(0, 0, 0, 0.5)";
    loadingOverlay.style.zIndex = "2000";
    loadingOverlay.style.display = "flex";
    loadingOverlay.style.justifyContent = "center";
    loadingOverlay.style.alignItems = "center";
    loadingOverlay.innerHTML = `<div style="color: white; font-size: 18px;">加载中...</div>`;
    document.body.appendChild(loadingOverlay);
}

// 隐藏加载中动画
export function hideLoading() {
    const loadingOverlay = document.getElementById("loading-overlay");
    if (loadingOverlay) {
        loadingOverlay.remove();
    }
}

// 初始化表格行数
export function initializeTableRows(tableElement, rowCount, columnHeaders = [], ptable = null, importModal=null) {
    if (!tableElement) {
        console.error("表格元素未找到，无法初始化行数");
        return;
    }
    if (!tableElement) {
        console.error("表格体未找到，无法初始化行数");
        return;
    }
    const isClean = tableElement.children.length === 0;
    const currentRowCount = 0;
    const tbody = document.createElement("tbody");
    if (isClean) {
        tableElement.innerHTML = "";
        // 创建表头
        const thead = document.createElement("thead");
        const headerRow = document.createElement("tr");
        columnHeaders.forEach(headerText => {
            const headerCell = document.createElement("th");
            headerCell.textContent = headerText;
            headerRow.appendChild(headerCell);
        });
        thead.appendChild(headerRow);
        tableElement.appendChild(thead);
        tableElement.appendChild(tbody);
    }   
    // 如果当前行数不足，则补充行
    for (let i = currentRowCount; i < rowCount; i++) {
        const newRow = document.createElement("tr");
        for (let j = 0; j < columnHeaders.length; j++) {
            const newCell = document.createElement("td");
            newCell.contentEditable = "true"; // 设置为可编辑
            styleCell(newCell); // 应用样式
            newRow.appendChild(newCell);
        }
        tbody.appendChild(newRow);
    }
    if(ptable)
    {
        const requiredFields = ptable.querySelectorAll("input"); 
        requiredFields.forEach((field) => {
            const name = field.name;
            // 选择浮窗内同名 input
            const input = importModal.querySelector(`input[name="${name}"]`);
            if (input) {
                input.value = field.value;
            }
        }); 
    }
}

// 处理粘贴事件，将数据填充到表格中
export function enableTablePaste(table, columncnt = 0) {

    if (!table) {
        console.error(`表格未找到: ${table}`);
        return;
    }

    table.addEventListener("paste", function (event) {
        event.preventDefault();

        // 获取粘贴内容
        const clipboardData = event.clipboardData || window.clipboardData;
        const pastedData = clipboardData.getData("text/plain");

        // 将粘贴内容解析为行和列
        const rows = pastedData.split("\n").filter(row => row.trim() !== "");
        const tableBody = table.querySelector("tbody");

        rows.forEach((row, rowIndex) => {
            const cells = row.split("\t"); // 使用制表符分隔列
            let tableRow = tableBody.children[rowIndex];

            // 如果当前行不存在，则创建新行
            if (!tableRow) {
                tableRow = document.createElement("tr");
                for (let i = 0; i < columncnt; i++) {
                    const newCell = document.createElement("td");
                    newCell.contentEditable = "true"; // 设置为可编辑
                    styleCell(newCell); // 应用样式
                    tableRow.appendChild(newCell);
                }
                tableBody.appendChild(tableRow);
            }

            cells.forEach((cellData, cellIndex) => {
                let tableCell = tableRow.children[cellIndex];

                // 如果当前单元格不存在，则创建新单元格
                if (!tableCell) {
                    tableCell = document.createElement("td");
                    tableCell.contentEditable = "true"; // 设置为可编辑
                    styleCell(tableCell); // 应用样式
                    tableRow.appendChild(tableCell);
                }

                // 填充单元格数据
                tableCell.textContent = cellData.trim();
            });
        });
    });
}

// 设置单元格样式
export function styleCell(cell) {
    cell.style.border = "1px solid #ccc";
    cell.style.padding = "8px";
    cell.style.minWidth = "100px";
}

// 动态添加行
export function addRow(tableBodySelector) {
    const tableBody = document.querySelector(tableBodySelector);
    if (!(tableBody instanceof HTMLElement)) {
        console.error("addRow: 参数 tableBody 必须是一个 DOM 元素");
        return;
    }

    const firstRow = tableBody.querySelector("tr");
    if (!firstRow) {
        console.error("addRow: 表格体中没有找到任何行");
        return;
    }

    const newRow = firstRow.cloneNode(true); // 克隆第一行
    const inputs = newRow.querySelectorAll("input, select");

    // 清空新行中的输入值
    inputs.forEach(input => {
        if (input.tagName === "INPUT") {
            input.value = "";
        } else if (input.tagName === "SELECT") {
            input.selectedIndex = 0;
        }
    });

    tableBody.appendChild(newRow); // 添加新行到表格体
}

// 删除行功能
export function enableRowDeletion(tableBodySelector) {
    const tableBody = document.querySelector(tableBodySelector);
    tableBody.addEventListener("click", function (event) {
        if (event.target.classList.contains("remove-row")) {
            const row = event.target.closest("tr");
            if (tableBody.children.length > 1) {
                row.remove();
            } else {
                alert("至少保留一行！");
            }
        }
    });
}

// 绑定快速填报的保存事件
export function bindQuickFillSave(button, url, csrfToken, getDataCallback, onSuccess, onError) {

    if (!button) {
        console.error(`按钮未找到: ${button}`);
        return;
    }

    button.addEventListener("click", function () {
        const data = getDataCallback(); // 获取数据的回调函数
        if (!data) {
            alert("请填写完整数据后再提交！");
            return;
        }

        showLoading();
        fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify(data)
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error("网络错误，保存失败！");
                }
                return response.json();
            })
            .then(result => {
                hideLoading(); // 隐藏加载中动画
                if (result.success) {
                    if (onSuccess) onSuccess(result); // 调用成功回调
                } else {
                    alert("保存失败：" + (result.message || "未知错误"));
                    if (onError) onError(result); // 调用失败回调
                }
            })
            .catch(error => {
                hideLoading(); // 隐藏加载中动画
                console.error("保存失败：", error);
                alert("保存失败：" + error.message);
                if (onError) onError(error); // 调用失败回调
            });
    });
}
// 从表格中提取数据，按列组织为列表
export function getTableData(table) {
    if (!table) {
        console.error(`表格未找到: ${table}`);
        return [];
    }

    const rows = table.querySelectorAll("tr");
    const data =  []; // 初始化列数组

    for (let row of rows) {
        const cells = row.getElementsByTagName("td");
        const rowData = [];
        for (let cell of cells) {
            if (cell.querySelector("select")) {
                rowData.push(cell.querySelector("select").value.trim());
            } else {
                rowData.push(cell.innerText.trim());
            }
            //console.log("单元格文本内容为：", rowData);
        }        
        //console.log("data内容为：", data);
        data.push(rowData);
    }
    return data.filter(row => row.some(cell => cell !== ""));
}

export function switchOverlay(overlay, modal, active) {
    console.log("switchOverlay:", active);
    if (active) {
        overlay.style.display = "block";
        modal.style.display = "block";
    } else {
        overlay.style.display = "none";
        modal.style.display = "none";
    }
}

export function toggleMaximizeModal(modalElement, maximizeButton, tableElement) {
    if (!modalElement || !maximizeButton) {
        console.error("无法找到模态框或最大化按钮");
        return;
    }
    const tableContainer = tableElement.parentElement

    maximizeButton.addEventListener("click", function () {
        if (modalElement.classList.contains("modal-maximized")) {
            // 如果已经是最大化状态，则还原
            modalElement.classList.remove("modal-maximized");
            maximizeButton.textContent = "⛶"; // 恢复按钮图标

            // 恢复表格容器的高度
            if (tableContainer) {
                tableContainer.style.height = "auto";
            }
        } else {
            // 否则将其设置为最大化
            modalElement.classList.add("modal-maximized");
            maximizeButton.textContent = "🗗"; // 更改按钮图标

            // 动态调整表格容器的高度
            const modalHeaderHeight = modalElement.querySelector(".modal-header").offsetHeight || 50;
            const modalFooterHeight = modalElement.querySelector(".modal-footer").offsetHeight || 50;
            const availableHeight = window.innerHeight - modalHeaderHeight - modalFooterHeight - 60; // 减去内边距
            tableContainer.style.height = `${availableHeight}px`;

            // 动态增加表格行数
            const rowHeight = 25; // 单元格高度
            const visibleRows = Math.floor(availableHeight / rowHeight); // 可见行数
            adjustTableRows(tableElement, visibleRows);
        }
    });
}


/**
 * 动态调整表格行数
 * @param {HTMLElement} tableElement 表格元素
 * @param {number} rowCount 需要显示的行数
 */
function adjustTableRows(tableElement, rowCount) {
    const tbody = tableElement.querySelector("tbody");
    if (!tbody) {
        console.error("表格中未找到 <tbody>");
        return;
    }

    const currentRowCount = tbody.children.length;

    // 如果当前行数不足，则补充行
    for (let i = currentRowCount; i < rowCount; i++) {
        const newRow = document.createElement("tr");
        const columnCount = tableElement.querySelectorAll("thead th").length || 1; // 获取列数
        for (let j = 0; j < columnCount; j++) {
            const newCell = document.createElement("td");
            newCell.textContent = ""; // 默认内容为空
            newRow.appendChild(newCell);
        }
        tbody.appendChild(newRow);
    }

    // 如果当前行数多于需要的行数，则移除多余的行
    for (let i = currentRowCount - 1; i >= rowCount; i--) {
        tbody.removeChild(tbody.children[i]);
    }
}

/**
 * 根据 MaterialGroup 的 Name 和 SubName 获取 parent_material 列表
 * @param {string} groupName - 物料组名称
 * @param {string} subName - 物料子组名称
 */
export function fetchParentMaterials(groupName, subName, material, selectElement) {
    // 如果未选择有效的 groupName，则清空 parent_material 下拉框
    if (groupName === "None") {
        Select.innerHTML = '<option value="None" selected>None</option>';
        return;
    }

    // 动态生成 URL
    const url = `${window.fetchParentMaterialsUrl}?group_name=${groupName}&sub_name=${subName}&material=${material}`;

    // 发送 AJAX 请求获取 parent_material 列表
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP 错误！状态码: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // 遍历 selectV 数据并生成 <option> 元素
                data.selectV.forEach(item => {
                    const option = document.createElement("option");
                    option.value = item.value; // 设置选项的值
                    option.textContent = item.text; // 设置选项的显示文本
                    selectElement.appendChild(option);
                });             
            } else {
                console.error("数据获取失败：", data.message);
            }
        })
        .catch(error => {
            console.error("请求失败：", error);
        });
}

export function mutationInputChange(input)
{
    if (input === null) {
        console.error(`未找到输入框`);
        return;
    }
    let oldValue = input.value;

    // 通过MutationObserver监听属性变化
    const observer = new MutationObserver(function(mutations) {
        if(input.value !== oldValue) {
            console.log('值变为:', input.value);
            oldValue = input.value;
            updateDropdownList(dropdownList, '值变为777');
        }
    });
    observer.observe(input, { attributes: true, childList: false, subtree: false });

    // 同时绑定常规事件
    input.addEventListener('input', function() {
        oldValue = this.value;
    });

    function updateDropdownList(dropdownList, value) {
        // 清空原有选项
        dropdownList.innerHTML = "";

        // 模拟根据输入值生成新选项
        const options = generateOptions(value);

        // 动态添加新选项
        options.forEach((option) => {
            const listItem = document.createElement("li");
            listItem.className = "el-select-dropdown__item";
            listItem.textContent = option.label;
            listItem.setAttribute("data-value", option.value);
            dropdownList.appendChild(listItem);
        });
    }

    /**
     * 模拟生成选项数据
     * @param {string} value 输入框的值
     * @returns {Array} 选项数组
     */
    function generateOptions(value) {
        if (!value) return [];
        return [
            { value: `${value}-1`, label: `选项 ${value}-1` },
            { value: `${value}-2`, label: `选项 ${value}-2` },
            { value: `${value}-3`, label: `选项 ${value}-3` },
        ];
    }
    
}

export function updataInputSelectOptions(input, subInput, subSubInput)
{
    mutationInputChange(input);
}

export function updateInput(source, target) {
    const sourceInput = table.querySelector('input[name="${source}"]');
    const targetInput = importModal.querySelector('input[name="${target}"]');
    if (sourceInput && targetInput) {
        targetInput.value = sourceInput.value;
    }
}

