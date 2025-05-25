from rest_framework import serializers
from .models import ChatRoom, Message, ChatNotification
from django.utils.timesince import timesince

class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(source='sender.email', read_only=True)
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    sender_role = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()
    is_own = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    unread_by = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ['id', 'chat_room', 'sender', 'sender_email', 'sender_name', 
                 'sender_role', 'content', 'message_type', 'image', 'image_url', 
                 'timestamp', 'unread_by', 'is_own']
        read_only_fields = ['id', 'timestamp', 'unread_by', 'sender', 'message_type']
    
    def get_sender_role(self, obj):
        if obj.sender:
            return 'admin' if obj.sender.is_staff else 'customer'
        return None
    
    def get_timestamp(self, obj):
        return timesince(obj.timestamp) + ' ago'
    
    def get_is_own(self, obj):
        request = self.context.get('request')
        return request and request.user == obj.sender
    
    def get_image_url(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None
    
    def get_unread_by(self, obj):
        return list(obj.unread_by) if obj.unread_by else []
    
    def validate(self, data):
        if self.context['request'].FILES.get('image'):
            data['message_type'] = Message.IMAGE
        return data

class ChatRoomSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    admin_name = serializers.CharField(source='admin.get_full_name', read_only=True, allow_null=True)
    unread_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'room_name', 'updated_at']
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            notification = ChatNotification.objects.filter(
                user=request.user,
                chat_room=obj
            ).first()
            return notification.count if notification else 0
        return 0
    
    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return MessageSerializer(last_message, context=self.context).data
        return None

class ChatNotificationSerializer(serializers.ModelSerializer):
    chat_room = ChatRoomSerializer(read_only=True)
    
    class Meta:
        model = ChatNotification
        fields = ['id', 'user', 'chat_room', 'count', 'last_updated']
        read_only_fields = ['id', 'last_updated']