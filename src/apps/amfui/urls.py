from django.urls import path
from . import views

app_name = 'amfui'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('home/', views.extend_home, name='home'),
    path('test/', views.test, name='test'),
]
