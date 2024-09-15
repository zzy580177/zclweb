from config.settings.components.common import URL_PREFIX

# SimpleUI 配置
SIMPLEUI_DEFAULT_THEME = 'purple.css'  # 默认主题
# SIMPLEUI_LOGO = f'/{URL_PREFIX}static/admin/images/custom_logo.png'
SIMPLEUI_HOME_PAGE = f'/{URL_PREFIX}admin/extend_home/'
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
}
SIMPLEUI_CONFIG = {
    'system_keep': True,  # 关闭系统菜单
    'menu_display': ['首页大屏','认证和授权','宏观质量', '品牌建设', '产品安全', '企业质量画像',
                     '企业基础设施','车间加工数据查看'],
    'dynamic': False,  # 设置是否开启动态菜单, 默认为False. 如果开启, 则会在每次用户登陆时动态展示菜单内容
    'menus': [{
        'name': '首页',
        'icon': 'fas fa-code',
        'url': 'https://gitee.com/tompeppa/simpleui',
        'codename': 'simpleui'
    }, {
        'name': '车间加工数据查看',
        'icon': 'fa fa-file',
        'codename': 'test',
        'models': [{
            'name': 'SimplePro',
            'icon': 'far fa-surprise',
            'models': [{
                'name': 'Pro文档',
                'url': 'https://simpleui.72wo.com/docs/simplepro'
            }, {
                'name': '购买Pro',
                'url': 'http://simpleui.72wo.com/simplepro'
            }]
        }, {
            'name': '社区',
            'url': 'https://simpleui.72wo.com',
            'icon': 'fab fa-github'
        }, {
            'name': '图片转换器',
            'url': 'https://convert.72wo.com',
            'icon': 'fab fa-github',
            'codename': 'nat'
        }]
    }]
}
