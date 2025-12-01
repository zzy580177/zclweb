export const T_ENDPOINTS = {
    '订单信息': 'order',
    '零件信息': 'part',
    '中间件信息': 'subpart',
    '规格参数': 'parm',
    '工艺线路': 'process',
    '子件工艺线路': 'process',
    'CNC工艺设计': 'cnc'
}
export const API_CONFIG = {
    'pmcui-porder':
    {
        '订单信息': {
            path: {GET:'/api/jihua/order/order'},
            params: ['OrderId']
        },
        '零件信息': {
            path: {GET:'/api/pmcui/parts_order/parts_list_by_order'},
            params: ['OrderId', 'FId']
        },
        '中间件信息': {
            path: {GET:'/api/bmui/material/submaterial'},
            params: ['FId']
        },
        '规格参数': {
            path: {GET:'/api/pmcui/material_parm/material_parm'},
            params: ['FId']
        },
        '工艺线路': {
            path: {GET:'/api/pmcui/process_step/router_processes/', POST:'/api/pmcui/process_step/check_update'},
            params: []
        },
        'CNC工艺设计': {
            path: {},
            params: []
        },
        '子件工艺线路':{
            path: {},
            params: []
        },
        route_get: {GET:'/api/pmcui/process_route/process_route_steps'},
        subPatrsMaterialLoad: {GET:'/api/pmcui/process_step_steps/route_subMaterial/'},
        step_transfer:{
            '中间件':{GET:'/api/bmui/material/submaterial'}, 
            'Other':{GET:'/api/pmcui/step/step'}},
        listPorderParts: {
            GET:'/api/pmcui/parts_order/parts_list_by_order', 
            PUT:'/api/pmcui/parts_order/update/',
            POST:'/api/pmcui/parts_order/create'
        }
    },
    'jihua':{
        order:{GET:'/api/jihua/order/order'}
    },
    'bmui':{
        material:{POST:'/api/bmui/material/material', GET:'/api/bmui/material/material'},
        material_group:{path:{GET:'/api/bmui/material_group/material_group'}, key:'FId', textK:'FName'},
        attribute:{path:{GET:'/api/bmui/attribute/list/'}, endpoint:'单位', key:'Id', textK:'Name'}
    },
    'a_wuliao':{
        attribute:{POST:'/api/a_wuliao/attribute/attribute'},
        group:{POST:'/api/a_wuliao/material_group/material_group'},
        material:{POST:'/api/a_wuliao/material/material'},
        version:{
            POST:'/api/a_wuliao/bom_version/bom_version', 
            GET:'/api/a_wuliao/bom_version/bom_version'},
        bom:{
            POST:'/api/a_wuliao/bom/bom', 
            GET:'/api/a_wuliao/bom_version/bom_version'},
    },
    'b_jihua':{
        order:{GET:'/api/b_jihua/order/order', POST:'/api/b_jihua/order/order', PUT:'/api/b_jihua/order/order'} ,
        order_parts:{
            GET:'/api/a_wuliao/bom_version/bom_version',
            POST:'/api/b_jihua/order_parts/order_parts', 
            PUT:'/api/b_jihua/order_parts/order_parts'},
        get_order_parts:{GET:'/api/b_jihua/order_parts/order_parts'},
    },
    'c_gongyi':{
        materialParm:{
            GET:'/api/a_wuliao/bom_version/bom_version',
            POST:'/api/c_gongyi/material_parm/material_parm', 
            PUT:'/api/c_gongyi/order/order'} ,        
        step:{
            GET:'/api/c_gongyi/step/step', POST:'/api/c_gongyi/step/step', 
            PUT:'/api/c_gongyi/step/step'} ,
        '订单信息': {
            path: {GET:'/api/b_jihua/order/order'},
            params: ['order_id']
        },
        '零件信息': {
            path: {GET:'/api/b_jihua/order_parts/order_parts'},
            params: ['order_id', 'material_id']
        },
        '中间件信息': {
            path: {GET:'/api/a_wuliao/bom/get_material_vi_parents'},
            params: ['material_id', 'version']
        },
        '规格参数': {
            path: {GET:'/api/c_gongyi/material_parm/material_parm'},
            params: ['material_id', 'version']
        },
        '工艺线路': {
                path: {GET:'/api/c_gongyi/process/route/', POST:'/api/c_gongyi/process/process'},
                params: []
        },
        'CNC工艺设计': {
            path: {},
            params: ['material_id', 'version']
        },
        lab_materials: {
            path: {GET:'/api/a_wuliao/bom/get_materials'},
            params: ['material_id', 'version']
        },
        route_selecter:{
            GET:'/api/c_gongyi/route/material',
            params: ['isCNC']
        },
        step_transfer:{
            '中间件':{GET:'/api/a_wuliao/bom/get_material_vi_parents'}, 
            'stepList':{GET:'/api/c_gongyi/step/step'}},

    },
    'd_gongyi':{
        materialParm:{
            GET:'/api/a_wuliao/bom_version/bom_version',
            POST:'/api/d_gongyi/material_parm/material_parm', 
            PUT:'/api/d_gongyi/order/order'} ,        
    }
};

export const H_ENDPOINTS = {
    'c_gongyi':{
        '订单信息': ['订单', '产品信息', '批次号', '订单状态', '截止日期'],
        '零件信息': ['组别', '物料编码', '物料名称', '规格型号', '版本信息', '生产单位', '生产数量', '零件当前状态', '交付截至'],
        '中间件信息': ['子件物料号','子件编码', '子件名称', '规格型号', '生产单位'],
        '规格参数': ['材料', '加工尺寸', '毛料尺寸', '镀层要求', '备注'],
        '工艺线路': ['工序序号', '类别', '工序列表', '加工参数', '备注','操作'],
        'CNC工艺设计': [],
        'main-filter': ['订单号','产品','批次']
    }
};

export const K_ENDPOINTS = {
    'c_gongyi':{
        '订单信息': ['order_id', 'product_id', 'lot_id', 'status', 'deadline'],
        '零件信息': ['material_group_name', 'material_number', 'material_name', 'material_model', 'version' ,'material_unit_name', 'quantity', 'status', 'deadline'],
        '中间件信息': ['material_id','material_number', 'material_name', 'material_model', 'material_unit_name'],
        '规格参数': ['stuff', 'size', 'cost', 'surface', 'description'],
        '工艺线路': ['seqnum', 'type_name', 'steps_step_ids', 'steps_step_names', 'steps_parms', 'description', '编辑'],
        'CNC工艺设计': [],
        'main-filter': ['order_id','product_id','lot_id']
    }
};

export const K_HIDDENS ={
    'c_gongyi':{
        '订单信息': [],
        '零件信息': [],
        '中间件信息': [],
        '规格参数': [],
        '工艺线路': ['steps_step_ids'],
        'CNC工艺设计': [],
        'main-filter': []
    }
};
export const BUTTON_NAME2ID ={
    '变更':'updata',
    '删除':'remove-row'
}


