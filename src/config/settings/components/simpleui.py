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
}
SIMPLEUI_CONFIG = {
    'system_keep': True,  # 关闭系统菜单
    'menu_display': ['首页大屏','认证和授权','宏观质量', '品牌建设', '产品安全', '企业质量画像',
                     '企业基础设施','数据看板','车间加工数据查看'],
    'dynamic': False,  # 设置是否开启动态菜单, 默认为False. 如果开启, 则会在每次用户登陆时动态展示菜单内容
    'menus': [{
        'name': '首页',
        'icon': 'fas fa-code',
        'url': 'https://gitee.com/tompeppa/simpleui',
        'codename': 'simpleui'
    }, {
        'name': '数据看板',
        'icon': 'fa fa-file',
        'codename': 'amfui',
        'models': [{
            'name': '设备看板',
            'icon': 'far fa-surprise',
            'url': '/amfui/dashboard/',
            'newTab': True,
        }]
    }]
}
