from config.settings.components.common import URL_PREFIX

# SimpleUI 配置
SIMPLEUI_DEFAULT_THEME = 'purple.css'  # 默认主题
# SIMPLEUI_LOGO = f'/{URL_PREFIX}static/admin/images/custom_logo.png'
SIMPLEUI_HOME_PAGE = f'/amfui/home/'
SIMPLEUI_HOME_ICON = 'fa fa-home'
SIMPLEUI_HOME_INFO = False  # 显示服务器信息
SIMPLEUI_HOME_QUICK = True  # 快速操作
SIMPLEUI_HOME_ACTION = True  # 最近动作
SIMPLEUI_ANALYSIS = False  # 关闭使用分析
SIMPLEUI_STATIC_OFFLINE = True  # 离线模式
SIMPLEUI_ICON = {
    '示例应用': 'fa fa-cat',
    '令牌': 'fa fa-lock',
    '认证令牌': 'fa fa-lock',
    '3.0 工艺参数': 'fa fa-sliders',
    '3.1 工序管理': 'fa fa-list-ol',
    '3.2 工艺卡': 'fa fa-clipboard',
    '3.3 工艺配方': 'fa fa-flask',
    '3.4 工艺流程': 'fa fa-project-diagram',
    '3.5 流程管理': 'fa fa-sitemap',
}
SIMPLEUI_CONFIG = {
    'system_keep': False,  # 关闭系统菜单
    'menu_display': ['首页大屏','认证和授权','宏观质量', '品牌建设', '产品安全', '企业质量画像',
                     '企业基础设施','数据看板','加工数据查看',
                     '生产计划管理','生产技术管理','基础资料管理','生产管理',
                     '01.基础资料','02.生产计划','03.生产工艺','04.加工中心',],  # 自定义菜单显示顺序
    'dynamic': False,  # 设置是否开启动态菜单, 默认为False. 如果开启, 则会在每次用户登陆时动态展示菜单内容
    'menus': [{
        'name': '首页',
        'icon': 'fas fa-code',
        'url': 'https://gitee.com/tompeppa/simpleui',
        'codename': 'simpleui'
    }, 
    {
        'name': '数据看板',
        'icon': 'fa fa-file',
        'codename': 'amfui',
        'models': [{
            'name': '设备看板',
            'icon': 'far fa-surprise',
            'url': '/amfui/dashboard/',
            'newTab': True,
        }]        
    },
    {
        'name': '01.基础资料',
        'icon': 'fa fa-database',
        'codename': 'a_wuliao',
        'models': [
            {
                'name': '1.0 基础属性',
                'icon': 'fa fa-boxes',
                'url': '/amf/a_wuliao/attribute/'
            },
            {
                'name': '1.1 物料组',
                'icon': 'fa fa-layer-group',
                'url': '/amf/a_wuliao/materialgroup/'
            },{
                'name': '1.2 物料档案',
                'icon': 'fa fa-cube',
                'url': '/amf/a_wuliao/material/'
            },{
                'name': '1.3 物料版本',
                'icon': 'fa fa-code-branch',
                'url': '/amf/a_wuliao/bomversion/'
            },{
                'name': '1.4 物料BOM',
                'icon': 'fa fa-sitemap',
                'url': '/amf/a_wuliao/bom/'
            }
        ]
    },
    {
        'name': '02.生产计划',
        'icon': 'fa fa-calendar-alt',
        'codename': 'b_jihua',
        'models': [
            {
                'name': '2.0 生产计划',
                'icon': 'fa fa-calendar-check',
                'url': '/amf/b_jihua/order/'
            },
            {
                'name': '2.1 生产任务单',
                'icon': 'fa fa-tasks',
                'url': '/amf/b_jihua/orderparts/'
            }
        ]
    },
    {
        'name': '03.生产工艺',
        'icon': 'fa fa-cogs',
        'codename': 'c_gongyi',
        'models': [
            {
                'name': '3.0 工艺参数',
                'icon': 'fa fa-sliders',
                'url': '/amf/c_gongyi/materialparm/'
            },
            {
                'name': '3.1 工序管理',
                'icon': 'fa fa-list-ol',
                'url': '/amf/c_gongyi/step/'
            },
            {
                'name': '3.2 产品工艺管理',
                'icon': 'fa fa-flask',
                'url': '/amf/c_gongyi/craft/'
            }
        ]
    },{
        'name': '04.加工中心',
        'icon': 'fa fa-industry',
        'codename': 'amfui',
        'models': [
            {
                'name': '4.0 设备管理',
                'icon': 'fa fa-toolbox',
                'url': '/amf/amfui/cell/'
            },{
                'name': '4.1 设备告警监控',
                'icon': 'fa fa-tachometer-alt',
                'url': '/amf/amfui/stato/'
            },{
                'name': '4.2 工单加工监控',
                'icon': 'fa fa-clipboard-list',
                'url': '/amf/amfui/worksheet/'
            },{
                'name': '4.3 加工日志',
                'icon': 'fa fa-database',
                'url': '/amf/amfui/record/'
            }
        ]
    }
    ]
}
