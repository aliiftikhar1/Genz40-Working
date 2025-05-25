"""
ASGI config for genz40 project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'genz40.settings')

# Initialize Django app registry
django_asgi_app = get_asgi_application()

# Import chat.routing *after* Django is initialized
from chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns
from mobileChat.urls import websocket_urlpatterns as mobile_websocket_urlpatterns

# Combine WebSocket URL patterns
websocket_urlpatterns = chat_websocket_urlpatterns + mobile_websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})