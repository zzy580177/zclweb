import os
from config.settings import BASE_DIR

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE':'mssql',
        'HOST':'47.121.177.127',
        'NAME':'amfAuth',
        'PORT':'1433',
        'USER':'amfAuth1234',
        'PASSWORD':'Zclamfdb1234',
        "SCHEMA": "CNC700Cutting",
        'OPTIONS':{
            'DRIVER':'SQL server Native Client 11.0',
            'encrypt': 'yes',
            'extra_params': 'TrustServerCertificate=yes'
        }
    },
    'ouhaidb': {
        'ENGINE':'mssql',
        'HOST':'47.121.177.127',
        'NAME':'ouhaidb',
        'PORT':'1433',
        'USER':'ouhai',
        'PASSWORD':'OH12345!',
        "SCHEMA": "CNC700Cutting",
        'OPTIONS':{
            'DRIVER':'SQL server Native Client 11.0',
            'encrypt': 'yes',
            'extra_params': 'TrustServerCertificate=yes'
        }
    },
    'yadi': {
        'ENGINE':'mssql',
        'HOST':'47.121.177.127',
        'NAME':'yadi',
        'PORT':'1433',
        'USER':'zclamf',
        'PASSWORD':'Zclamfdb123',
        "SCHEMA": "CNC700Cutting",
        'OPTIONS':{
            'DRIVER':'SQL server Native Client 11.0',  # 指定新版本驱动
            'encrypt': 'yes',
            'extra_params': 'TrustServerCertificate=yes'
        }
    },
    'zcl': {
        'ENGINE':'mssql',
        'HOST':'47.121.177.127',
        'NAME':'zcl',
        'PORT':'1433',
        'USER':'zclamf',
        'PASSWORD':'Zclamfdb123',
        "SCHEMA": "CNC700Cutting",
        'OPTIONS':{
            'DRIVER':'SQL server Native Client 11.0',  # 指定新版本驱动
            'encrypt': 'yes',
            'extra_params': 'TrustServerCertificate=yes'
        }
    },
    'okia': {
        'ENGINE':'mssql',
        'HOST':'47.121.177.127',
        'NAME':'okia',
        'PORT':'1433',
        'USER':'okia',
        'PASSWORD':'Okia2541!',
        "SCHEMA": "CNC700Cutting",
        'OPTIONS':{
            'DRIVER':'SQL server Native Client 11.0',  # 指定新版本驱动
            'encrypt': 'yes',
            'extra_params': 'TrustServerCertificate=yes'
        }
    },
}
DATABASE_ROUTERS =['django_starter.middleware.database_router.DatabaseRouter']
DATABASE_APPS_MAPPING = {
    'default':'default',
    'yadi':'yadi',
    'zcltest':'zcl',
    'OKIAVN':'okia',
}
SCHEMA_MAPPING = {
    'default_schema': 'CNC700Cutting',
    'OKIAVN': 'CNC700Cutting',
    'pmcui': 'base',
    'bmui': 'base',
    'a_wuliao': 'base'
}

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
