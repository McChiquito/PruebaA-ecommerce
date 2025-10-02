# productos/urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import ProductoAPIView, subir_catalogo_dashboard, admin_dashboard_view

app_name = 'productos'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/productos/', ProductoAPIView.as_view(), name='productos-api'),
    path('upload-excel/', views.upload_excel_view, name='upload_excel_page'), # Solo una vez
   # path('start-chat/', views.start_chat_view, name='start_chat'),
  #  path('api/conversations/<int:conversation_id>/close/', views.close_conversation_api, name='close_conversation_api'),
  #  path('admin-chat/', views.admin_chat_panel, name='admin_chat_panel'),
 #   path('admin-chat/<int:conversation_id>/', views.admin_chat_panel, name='admin_chat_panel_detail'),
    path('subir-catalogo-dashboard/', subir_catalogo_dashboard, name='subir_catalogo_dashboard'),
    path('admin-dashboard/', admin_dashboard_view, name='admin_dashboard'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



