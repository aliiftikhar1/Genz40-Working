from django.urls import path
from . import views
from . import consumers

urlpatterns = [
    path('rooms/', views.ChatRoomListCreateView.as_view(), name='chatroom-list-create'),
    path('rooms/list/', views.ChatRoomListCreateView.as_view(), name='chatroom-list'),
    path('rooms/<int:room_id>/messages/', views.MessageListCreateView.as_view(), name='message-list-create'),
    path('rooms/<int:room_id>/unread/', views.UnreadMessagesView.as_view(), name='unread-messages'),
    path('rooms/<int:room_id>/read/', views.MarkMessagesAsReadView.as_view(), name='mark-read'),
    path('notifications/', views.ChatNotificationListView.as_view(), name='notification-list'),
    path('community/rooms/', views.CommunityChatRoomListView.as_view(), name='community-chatroom-list'),
    path('upload-image/', views.ImageUploadView.as_view(), name='upload-chat-image')
]

websocket_urlpatterns = [
    path('ws/chat/<int:room_id>/', consumers.ChatConsumer.as_asgi()),
    path('ws/chat/global/', consumers.GlobalChatConsumer.as_asgi()),
]