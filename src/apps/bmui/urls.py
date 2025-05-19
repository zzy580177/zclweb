from django.urls import path
from . import views

urlpatterns = [
    path('save-boms/', views.save_boms, name='save_boms'),
    path('save-attributes/', views.save_attributes, name='bmui_attribute_save'),
    path('get-versions/', views.get_versions, name='get_versions'),  # 新增获取版本列表的路由
    #path('get-parent-materials/', views.get_parent_materials, name='get_parent_materials'),  # 新增路由

]