import { API_CONFIG} from './apiConfig.js'

export class utils
{

    static switchOverlay(modal, active) {
        if (!modal) return; // 提前终止无效调用
        
        const overlay = modal.nextElementSibling;
        const displayValue = active ? "block" : "none";
        
        modal.style.display = displayValue;
        if (overlay) overlay.style.display = displayValue;
    }
    static maximizeModal(modal, mainID_context) {
        const maximizeButton = modal.querySelector("#maximize-modal");
        if (!maximizeButton) {
            console.error("无法找到模态框或最大化按钮");
            return;
        }
        const mainbody = modal.querySelector(mainID_context);
        if (modal.classList.contains("modal-maximized")) {
            modal.classList.remove("modal-maximized");
            maximizeButton.textContent = "⛶";
            if (mainbody) {
                modal.style.maxHeight = '80vh';
                mainbody.style.maxHeight = '70vh';
            }
        } else {
            modal.classList.add("modal-maximized");
            maximizeButton.textContent = "🗗";
            if (mainbody) {
                modal.style.maxHeight = '100vh';
                mainbody.style.maxHeight = '90vh';
            }
        }

    }

    static setDataset(container, dataObj) {
        Object.entries(dataObj).forEach(([key, value]) => {
            const dataKey = key;
            container.dataset[dataKey] = value;
        });
        return dataObj;
    }

    static datasetToObj(element) {
        if (!element || !element.dataset) {
            console.warn('无效的DOM元素或元素没有dataset属性');
            return {};
        }
        const result = {};
        const dataset = element.dataset;
        for (const key in dataset) {
            if (Object.prototype.hasOwnProperty.call(dataset, key)) {
                const camelCaseKey = key;
                result[camelCaseKey] = dataset[key];
            }
        }        
        return result;
    }
    static parseContainerAttr(container, attrName) {
        try {
            const normalizedAttr = attrName.replace(/[A-Z]/g, match => `-${match.toLowerCase()}`);
            return JSON.parse(container.getAttribute(normalizedAttr) || null);
        } catch {
            return null;
        }
    }
    static getValueByPath(obj, path, fallback) {
        if (typeof obj !== 'object' || obj === null) {
            return fallback || obj;
        }        
        return path?.split('.').reduce((acc, key) => 
            (acc && acc[key] !== undefined) ? acc[key] : fallback||'', obj);
    }

    static getSelectedCellValue(selected, keys) {
        // 参数验证
        if (!selected || !keys || !Array.isArray(keys)) return null;    
        let tr = selected.closest('tr');
        if (!tr || tr.parentNode.tagName.toLowerCase() !== 'tbody') return null;
        const cells = Array.from(tr.children);
        const result = {};    
        keys.forEach(key => {
            const cell = cells.find(cell => cell.getAttribute('data-key') === key);
            if (cell) {
                const attrValue = cell.getAttribute('data-key');
                if (attrValue) {
                    const finalKey = attrValue.split('.').at(-1);
                    result[finalKey] = cell.textContent.trim();
                }
            }
        });
        
        return Object.keys(result).length > 0 ? result : null;
    }

}
export class loadingOverlay {
    static show() {
        const overlay = document.createElement("div");
        overlay.id = "loading-overlay";
        overlay.style.position = "fixed";
        overlay.style.top = "0";
        overlay.style.left = "0";
        overlay.style.width = "100%";
        overlay.style.height = "100%";
        overlay.style.backgroundColor = "rgba(0, 0, 0, 0.5)";
        overlay.style.zIndex = "2000";
        overlay.style.display = "flex";
        overlay.style.justifyContent = "center";
        overlay.style.alignItems = "center";
        overlay.innerHTML = `<div style="color: white; font-size: 18px;">加载中...</div>`;
        document.body.appendChild(overlay);
    }

    static hide() {
        const overlay = document.querySelector('#loading-overlay');
        if (overlay) {
            overlay.remove();
        } else {
            console.warn('未找到加载覆盖层元素');
        }
    }
}

export class URLConfig{
    static buildApiParams(config,  order_part) {
        if (!config) return '';
        const url_params = {}
        config.params.forEach(param => {
            url_params[param] = order_part[param] ;
        })
        if(url_params.FID) url_params.FID = parseInt(url_params.FID)
        return url_params;
    }

    static bindApiUrl(resourceKey, title = '', bindStr = '') {
        let config = API_CONFIG[resourceKey]
        config = config[title];
        if (!config?.path) return '';
        
        // 处理路径拼接规范
        const basePath = config.path.endsWith('/') 
            ? config.path.slice(0, -1) 
            : config.path;
        
        const boundPath = bindStr.startsWith('/')
            ? bindStr.slice(1)
            : bindStr;
        
        return `${basePath}/${boundPath}`.replace(/\/+/g, '/');
    }
}
