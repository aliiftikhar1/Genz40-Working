"""
URL configuration for genz40 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from genz40 import custom_sortable_urls
from django.urls import path, re_path
from chat import views
from chat.consumers import ChatConsumer
from chat.urls import websocket_urlpatterns as chat_websocket_urlpatterns
from mobileChat.urls import websocket_urlpatterns as mobile_websocket_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('admin/backend/postnavitem/', include(custom_sortable_urls)),
    path('', include('frontend.urls')),
    path('auth/', include('backend.urls')),
    path('api/chat/', include('chat.urls')),
    path('mobile/chat/', include('mobileChat.urls'))
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Combine both web and mobile WebSocket URL patterns
websocket_urlpatterns = chat_websocket_urlpatterns + mobile_websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})