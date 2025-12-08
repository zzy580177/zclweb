import { API_CONFIG} from './apiConfig.js'

export class utils
{
    
    static updateDict(dict1, dict2) {
        for (const key in dict2) {
            if (dict1.hasOwnProperty(key)) {
            dict1[key] = dict2[key];  // 更新匹配字段
            }
        }
        return dict1;
    }


    static switchOverlay(modal, active) {
        if (!modal) return; // 提前终止无效调用
        const overlay = document.getElementById(`${modal.id}-overlay`);
        const displayValue = active ? "block" : "none";

        modal.style.display = displayValue;
        if (overlay) overlay.style.display = displayValue;

        // 多浮窗层级管理
        //if (active) {
        //    ModalStackManager.pushModal(modal);
        //} else {
        //    ModalStackManager.removeModal(modal);
        //}
    }

    /**
     * 专门用于多浮窗切换的管理方法
     * @param {Element} modal - 要显示的模态框
     * @param {Array} closeOthers - 是否关闭其他模态框的ID数组
     */
    static switchOverlayMulti(modal, active, closeOthers = []) {
        if (!modal) return;

        // 如果需要关闭其他模态框
        if (active && closeOthers.length > 0) {
            closeOthers.forEach(modalId => {
                const otherModal = document.getElementById(modalId);
                if (otherModal && otherModal.style.display !== 'none') {
                    this.switchOverlay(otherModal, false);
                }
            });
        }

        this.switchOverlay(modal, active);
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

/**
 * 模态框堆栈管理器
 * 负责管理多浮窗的层级和显示状态
 */
export class ModalStackManager {
    static modalStack = [];

    /**
     * 添加模态框到堆栈
     * @param {Element} modal - 模态框元素
     */
    static pushModal(modal) {
        if (!modal) return;

        // 移除已在堆栈中的相同模态框
        this.removeModal(modal);

        // 添加到堆栈顶部
        this.modalStack.push(modal);

        // 更新z-index层级
        this.updateZIndexes();
    }

    /**
     * 从堆栈中移除模态框
     * @param {Element} modal - 模态框元素
     */
    static removeModal(modal) {
        if (!modal) return;

        const index = this.modalStack.indexOf(modal);
        if (index > -1) {
            this.modalStack.splice(index, 1);
        }

        // 更新z-index层级
        this.updateZIndexes();
    }

    /**
     * 更新所有模态框的z-index层级
     */
    static updateZIndexes() {
        const baseZIndex = 10000;

        this.modalStack.forEach((modal, index) => {
            if (modal && modal.style) {
                modal.style.zIndex = (baseZIndex + index).toString();

                // 同时更新对应的遮罩层z-index
                const overlay = modal.nextElementSibling;
                if (overlay && overlay.classList.contains('modal-overlay')) {
                    overlay.style.zIndex = (baseZIndex + index - 1).toString();
                }
            }
        });
    }

    /**
     * 获取当前顶层模态框
     * @returns {Element|null} 顶层模态框
     */
    static getTopModal() {
        return this.modalStack.length > 0 ? this.modalStack[this.modalStack.length - 1] : null;
    }

    /**
     * 关闭所有模态框
     */
    static closeAllModals() {
        while (this.modalStack.length > 0) {
            const modal = this.modalStack.pop();
            if (modal) {
                modal.style.display = 'none';
                const overlay = modal.nextElementSibling;
                if (overlay) overlay.style.display = 'none';
            }
        }
    }

    /**
     * 检查模态框是否在堆栈中
     * @param {Element} modal - 模态框元素
     * @returns {boolean} 是否在堆栈中
     */
    static isInStack(modal) {
        return this.modalStack.includes(modal);
    }

    /**
     * 获取堆栈的大小
     * @returns {number} 堆栈大小
     */
    static getStackSize() {
        return this.modalStack.length;
    }
}
