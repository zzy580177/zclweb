from django.urls import path
from . import views

app_name = 'amfui'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('home/', views.extend_home, name='home'),
    path('test/', views.test, name='test'),
    path('worksheet/', views.worksheet_view, name='worksheet_view'),
    path('worksheet/manage/', views.worksheet_manage_view, name='worksheet_manage_view'),
    path('worksheet/delete/<str:worksheet_id>/', views.delete_worksheet, name='delete_worksheet'),
    path('order/delete/', views.delete_order, name='delete_order'),
    path('order/new_order', views.new_order, name='new_order'),
]
