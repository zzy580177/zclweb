from django.contrib import admin
from django.urls import path, include

# DjangoStarter 主页
from django_starter.contrib.guide import views

from config.apis import api

urlpatterns = [
    #path('', views.index),
    path('api/', api.urls),
    path('amfui/', include('apps.amfui.urls')),

    # DjangoStarter, django-starter/
    #path('', include('django_starter.urls')),

    # 管理后台

    path('amf/', include('django_starter.contrib.admin.urls')),  # 实现 admin 登录验证码
    path('amf/', admin.site.urls),
    # 验证码
    path('captcha/', include('captcha.urls')),
]
