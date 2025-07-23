# productos/urls.py
from django.urls import path
from . import views
from .views import ProductoAPIView

app_name = 'productos'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/productos/', ProductoAPIView.as_view(), name='productos-api'),
    path('upload-excel/', views.upload_excel_view, name='upload_excel_page'), # Solo una vez
   # path('start-chat/', views.start_chat_view, name='start_chat'),
  #  path('api/conversations/<int:conversation_id>/close/', views.close_conversation_api, name='close_conversation_api'),
  #  path('admin-chat/', views.admin_chat_panel, name='admin_chat_panel'),
 #   path('admin-chat/<int:conversation_id>/', views.admin_chat_panel, name='admin_chat_panel_detail'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
]