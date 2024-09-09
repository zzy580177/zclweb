import os
from config.settings import BASE_DIR

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE':'mssql',
        'HOST':'47.121.177.127',
        'NAME':'zcl',
        'PORT':'1433',
        'USER':'zclamf',
        'PASSWORD':'Zclamfdb123',
        'OPTIONS':{
            'DRIVER':'SQL server Native Client 11.0',
        }
    },
    'default1': {
        'ENGINE':'mssql',
        'HOST':'47.121.177.127',
        'NAME':'amfAuth',
        'PORT':'1433',
        'USER':'amfAuth1234',
        'PASSWORD':'Zclamfdb1234',
        'OPTIONS':{
            'DRIVER':'SQL server Native Client 11.0',
        }
    },
    'yadi': {
        'ENGINE':'mssql',
        'HOST':'47.121.177.127',
        'NAME':'yadi',
        'PORT':'1433',
        'USER':'zclamf',
        'PASSWORD':'Zclamfdb123',
        'OPTIONS':{
            'DRIVER':'SQL server Native Client 11.0',
        }
    },
    'jinya': {
        'ENGINE':'mssql',
        'HOST':'47.121.177.127',
        'NAME':'jinya',
        'PORT':'1433',
        'USER':'zclamf',
        'PASSWORD':'Zclamfdb123',
        'OPTIONS':{
            'DRIVER':'SQL server Native Client 11.0',
        }
    }
}
DATABASE_ROUTERS =['apps.amfui.middleware.database_router.DatabaseRouter']
DATABASE_APPS_MAPPING = {
    'default':'default',
    'yadi':'yadi',
    'jinya':'jinya',
}

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
