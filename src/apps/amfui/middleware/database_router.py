from django.conf import settings
from django.db import connections
from ..urls import app_name
DATABASES_MAPPING = settings.DATABASE_APPS_MAPPING

class DatabaseRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == app_name:
            user = getattr(settings, 'LOGGED_IN_USER', None)  # 获取当前登录用户
            if user:
                db_name = f'{user.username}'  # 根据用户名生成数据库名
                return db_name if db_name in settings.DATABASES else None
        return None
 
    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)
 
    def allow_relation(self, obj1, obj2, **hints):
        db_list = [db for db in [self.db_for_read(obj1), self.db_for_read(obj2)] if db]
        return db_list == [db_list[0]] if db_list else True
 
    def allow_syncdb(self, db, model):
        return db in self.db_for_write(model)