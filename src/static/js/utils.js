import { API_CONFIG} from './apiConfig.js'

export class utils
{
    static switchOverlay(modal, active) {
        const overlay = modal.nextElementSibling;
        if (active) {
            modal.style.display = "block";
            if(overlay) overlay.style.display = "block";
        } else {
            modal.style.display = "none";
            if(overlay) overlay.style.display = "none";
        }
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
                mainbody.style.maxHeight = '60vh';
            }
        } else {
            modal.classList.add("modal-maximized");
            maximizeButton.textContent = "🗗";
            if (mainbody) {
                mainbody.style.maxHeight = '';
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
    static getValueByPath(obj, path, fallback = '') {
        return path?.split('.').reduce((acc, key) => 
            (acc && acc[key] !== undefined) ? acc[key] : fallback, obj);
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
    static buildApiParams(resourceKey, title = '', order_part) {
        let config = API_CONFIG[resourceKey]
        config = config[title];    
        if (!config) return '';
        const url_params = {}
        config.params.forEach(param => {
            url_params[param] = order_part[param.replace('OrderId', 'POrder_id')] ;
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
