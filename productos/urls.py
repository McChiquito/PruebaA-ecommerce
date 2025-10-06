# productos/urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import ProductoAPIView, vista_catalogo

app_name = 'productos'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/productos/', ProductoAPIView.as_view(), name='productos-api'),
    path('admin/upload-catalogs/', views.upload_catalogs_view, name='upload_catalogs'),
   # path('start-chat/', views.start_chat_view, name='start_chat'),
  #  path('api/conversations/<int:conversation_id>/close/', views.close_conversation_api, name='close_conversation_api'),
  #  path('admin-chat/', views.admin_chat_panel, name='admin_chat_panel'),
 #   path('admin-chat/<int:conversation_id>/', views.admin_chat_panel, name='admin_chat_panel_detail'),
    path('admin-chat-panel/', views.admin_chat_panel, name='admin_chat_panel'),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path('', vista_catalogo, name='vista_catalogo'),

]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



