# ecommerce_project/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import productos.routing # <--- Asegúrate de que esta línea esté presente

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # Esto manejará conexiones WebSocket
    "websocket": AuthMiddlewareStack(
        URLRouter(
            productos.routing.websocket_urlpatterns
        )
    ),
})