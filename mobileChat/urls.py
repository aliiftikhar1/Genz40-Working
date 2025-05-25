from django.urls import re_path, path
from . import consumers
from . import views

urlpatterns = [
    # Chat Rooms
    path('rooms/', views.MobileChatRoomListView.as_view(), name='mobile-chatroom-list'),
    
    # Messages
    path('rooms/<int:room_id>/messages/', views.MobileMessageListCreateView.as_view(), name='mobile-message-list-create'),
    path('rooms/<int:room_id>/read/', views.MobileMarkMessagesAsReadView.as_view(), name='mobile-mark-messages-read'),
    
    # Notifications
    path('notifications/', views.MobileChatNotificationListView.as_view(), name='mobile-notification-list'),
    
    # Media
    path('upload-image/', views.MobileImageUploadView.as_view(), name='mobile-upload-chat-image'),
]

websocket_urlpatterns = [
    re_path(r"ws/mobilechat/user/(?P<token>[^/]+)/$", consumers.MobileChatConsumer.as_asgi()),
]