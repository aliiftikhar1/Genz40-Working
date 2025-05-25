# from django.contrib import admin
# from .models import ChatRoom, Message, ChatNotification

# @admin.register(ChatRoom)
# class ChatRoomAdmin(admin.ModelAdmin):
#     list_display = ('room_name', 'chat_type', 'customer', 'admin', 'is_active', 'updated_at')
#     list_filter = ('chat_type', 'is_active')
#     search_fields = ('room_name', 'subject', 'customer__email', 'admin__email')

# @admin.register(Message)
# class MessageAdmin(admin.ModelAdmin):
#     list_display = ('chat_room', 'sender', 'message_type', 'timestamp', 'is_read')
#     list_filter = ('message_type', 'is_read')
#     search_fields = ('content', 'sender__email')

# @admin.register(ChatNotification)
# class ChatNotificationAdmin(admin.ModelAdmin):
#     list_display = ('user', 'chat_room', 'count', 'last_updated')
#     search_fields = ('user__email',)