from django.urls import path
from . import views

urlpatterns = [
    path('quick-fill/', views.quick_fill, name='bmui_quick_fill'),
    path('api/materialgroup/fgroupcode/', views.get_fgroupcode_options, name='get_fgroupcode_options'),
    path('save-attributes/', views.save_attributes, name='bmui_attribute_save'),
    #path('get-parent-materials/', views.get_parent_materials, name='get_parent_materials'),  # 新增路由

]