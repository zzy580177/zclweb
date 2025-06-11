export function bindInputsForFilter(orderId,inputs) {
    let detail = [];
    let params = [];
    if (orderId) 
        detail.push(`订单号: ${orderId}`);
        params.push('OrderId=' + encodeURIComponent(orderId));
    inputs.forEach(key => {
        const val = document.querySelector('input[name="' + key + '"]').value.trim();
        if (val) 
            detail.push(`${key}: ${val}`);
            params.push(key + "=" + encodeURIComponent(val));
    })                
    document.getElementById('filter-detail-content').textContent = detail.length ? detail.join('，') : '无';
    return params
}

export function getSelectedCellValue(ids, selected) {
    let tr = selected.target.closest('tr');
    if (!tr || tr.parentNode.tagName.toLowerCase() !== 'tbody') return null;
    // 假设订单号在第一列
    let result =[]
    for (let i = 0; i < ids.length; i++) {
        result.push(tr.children[ids[i]].textContent.trim());
    }
    return result;
}

export function renderTitleDiv(containerId, textContent) {
    //const titleTextDiv = document.querySelector('.title-text');  
    const titleTextDiv = document.querySelector(containerId);
    if (titleTextDiv) {
        titleTextDiv.textContent = textContent;
        titleTextDiv.setAttribute('title', textContent);
    }
}