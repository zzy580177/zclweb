import {fastFillModelRenderer } from './renderFrame.js';
import {fetchDataRenderFrame} from './eventAction.js';

export function renderFastFillModel(container, select_params, table_params){
    const renderer = new fastFillModelRenderer(container, select_params, table_params);    
    renderer.render()
}