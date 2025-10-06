# ecommerce_project/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import os

urlpatterns = [
    re_path(r'^favicon\.ico$', serve, {
        'path': 'favicon.ico',
        'document_root': os.path.join(settings.STATIC_ROOT),
    }),

    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    # 👇 ESTA LÍNEA hace que la raíz "/" cargue las URLs de productos
    path('', include(('productos.urls', 'productos'), namespace='productos')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
