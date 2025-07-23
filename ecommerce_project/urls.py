# ecommerce_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Esta línea es crucial para la URL raíz, e incluye todas las URLs de tu app 'productos'
    path('', include('productos.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('productos/', include('productos.urls', namespace='productos')), # <-- Solo una de estas líneas con namespace='productos'

    
    # ELIMINA o COMENTA LA SIGUIENTE LÍNEA SI LA TIENES AQUÍ:
    # path('start-chat/', views.start_chat_view, name='start_chat'), 
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
