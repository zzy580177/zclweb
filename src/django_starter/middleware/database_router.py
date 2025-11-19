from django.conf import settings
from django.db import connections
DATABASES_MAPPING = settings.DATABASE_APPS_MAPPING
apps=['amfui',  'bmui','pmcui', 'jihuaManagerUI', 'a_wuliao', 'b_jihua', 'c_gongyi']

class DatabaseRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label in apps:
            user = getattr(settings, 'LOGGED_IN_USER', None)  # 获取当前登录用户
            if user:
                db_name = f'{DATABASES_MAPPING[user.username]}'  # 根据用户名生成数据库名
                return db_name if db_name in settings.DATABASES else None
        return None
 
    def db_for_write(self, model, **hints):
        if model._meta.app_label in apps:
            user = getattr(settings, 'LOGGED_IN_USER', None)  # 获取当前登录用户
            if user:
                db_name = f'{DATABASES_MAPPING[user.username]}'    # 根据用户名生成数据库名
                return db_name if db_name in settings.DATABASES else None
        return None
 
    def allow_relation(self, obj1, obj2, **hints):
        db_list = [db for db in [self.db_for_read(obj1), self.db_for_read(obj2)] if db]
        return db_list == [db_list[0]] or [db_list[1]] == [db_list[0]] if db_list else True
 
    def allow_syncdb(self, db, model):
        return db in self.db_for_write(model)