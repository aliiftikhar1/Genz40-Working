from rest_framework import serializers
from chat.models import ChatRoom, Message, ChatNotification
from backend.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'full_name']

class ChatRoomSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    admin = UserSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'room_name', 'subject', 'chat_type', 'customer', 'admin', 
                 'last_message', 'updated_at', 'created_at']

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-timestamp').first()
        if last_message:
            return {
                'id': last_message.id,
                'content': last_message.content,
                'timestamp': last_message.timestamp,
                'sender': UserSerializer(last_message.sender).data if last_message.sender else None,
                'message_type': last_message.message_type,
                'image_url': last_message.image.url if last_message.image else None
            }
        return None

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'content', 'sender', 'timestamp', 'is_read', 
                 'message_type', 'image_url']

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

class ChatNotificationSerializer(serializers.ModelSerializer):
    chat_room = ChatRoomSerializer(read_only=True)

    class Meta:
        model = ChatNotification
        fields = ['id', 'chat_room', 'count', 'created_at'] 