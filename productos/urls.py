from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import ProductoAPIView, upload_catalogs_view, admin_chat_panel, admin_dashboard

app_name = 'productos'

urlpatterns = [
    path('', views.index, name='index'),  # 👉 Página principal con el catálogo incluido
    path('api/productos/', views.api_productos, name='api_productos'),
    path('admin-dashboard/upload-catalogs/', upload_catalogs_view, name='upload_catalogs'),
    path('admin-chat-panel/', admin_chat_panel, name='admin_chat_panel'),
    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
    path('', views.catalogo_view, name='catalogo'),
    path("", views.vista_principal, name="inicio"),
]

# Archivos estáticos y media
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
