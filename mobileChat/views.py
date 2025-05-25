from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from chat.models import ChatRoom, Message, ChatNotification
from chat.serializers import ChatRoomSerializer, MessageSerializer, ChatNotificationSerializer
from django.db.models import Q, Max
from django.utils import timezone
import jwt
from django.conf import settings
from rest_framework.parsers import MultiPartParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

class JWTAuthentication(permissions.BasePermission):
    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return False
        
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            if user_id:
                request.user = get_user_model().objects.get(id=user_id)
                return True
        except (jwt.InvalidTokenError, get_user_model().DoesNotExist):
            return False
        return False

class MobileChatRoomListView(generics.ListAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [JWTAuthentication]

    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(
            Q(customer=user) | Q(admin=user) | Q(members=user)
        ).annotate(
            last_message_time=Max('messages__timestamp')
        ).order_by('-last_message_time', '-updated_at')

class MobileMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [JWTAuthentication]

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        chat_room = ChatRoom.objects.get(id=room_id)
        if chat_room.chat_type == ChatRoom.COMMUNITY:
            if not chat_room.members.filter(id=self.request.user.id).exists():
                return Message.objects.none()
        return Message.objects.filter(
            chat_room_id=room_id
        ).select_related('sender').order_by('timestamp')

    def perform_create(self, serializer):
        room_id = self.kwargs['room_id']
        chat_room = ChatRoom.objects.get(id=room_id)
        if chat_room.chat_type == ChatRoom.COMMUNITY:
            if not chat_room.members.filter(id=self.request.user.id).exists():
                raise ValueError("User is not a member of this community")
        message = serializer.save(
            sender=self.request.user, 
            chat_room=chat_room
        )
        
        chat_room.update_timestamp()
        
        if chat_room.chat_type == ChatRoom.COMMUNITY:
            for member in chat_room.members.exclude(id=self.request.user.id):
                notification, created = ChatNotification.objects.get_or_create(
                    user=member,
                    chat_room=chat_room,
                    defaults={'count': 1}
                )
                if not created:
                    notification.increment()
        else:
            recipient = chat_room.admin if self.request.user == chat_room.customer else chat_room.customer
            if recipient:
                notification, created = ChatNotification.objects.get_or_create(
                    user=recipient,
                    chat_room=chat_room,
                    defaults={'count': 1}
                )
                if not created:
                    notification.increment()

class MobileChatNotificationListView(generics.ListAPIView):
    serializer_class = ChatNotificationSerializer
    permission_classes = [JWTAuthentication]

    def get_queryset(self):
        return ChatNotification.objects.filter(
            user=self.request.user,
            count__gt=0
        ).select_related('chat_room')

class MobileImageUploadView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [JWTAuthentication]

    def post(self, request, *args, **kwargs):
        try:
            if 'image' not in request.FILES:
                return Response(
                    {'error': 'No image provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            image = request.FILES['image']
            room_id = request.data.get('room_id')

            if not room_id:
                return Response(
                    {'error': 'Room ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate room access
            chat_room = ChatRoom.objects.get(id=room_id)
            if chat_room.chat_type == ChatRoom.COMMUNITY:
                if not chat_room.members.filter(id=request.user.id).exists():
                    return Response(
                        {'error': 'Not authorized to access this room'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            elif not (request.user == chat_room.customer or request.user == chat_room.admin):
                return Response(
                    {'error': 'Not authorized to access this room'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Save image
            file_name = f"chat_images/{room_id}/{timezone.now().timestamp()}_{image.name}"
            file_path = default_storage.save(file_name, ContentFile(image.read()))
            file_url = default_storage.url(file_path)

            # Create message
            message = Message.objects.create(
                chat_room=chat_room,
                sender=request.user,
                content='Image shared',
                message_type=Message.IMAGE,
                image=file_path
            )

            # Create notification
            if chat_room.chat_type == ChatRoom.COMMUNITY:
                for member in chat_room.members.exclude(id=request.user.id):
                    notification, created = ChatNotification.objects.get_or_create(
                        user=member,
                        chat_room=chat_room,
                        defaults={'count': 1}
                    )
                    if not created:
                        notification.increment()
            else:
                recipient = chat_room.admin if request.user == chat_room.customer else chat_room.customer
                if recipient:
                    notification, created = ChatNotification.objects.get_or_create(
                        user=recipient,
                        chat_room=chat_room,
                        defaults={'count': 1}
                    )
                    if not created:
                        notification.increment()

            # Broadcast the message to the WebSocket group
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'chat_{room_id}',
                {
                    'type': 'chat_message',
                    'id': str(message.id),
                    'message': message.content,
                    'sender_id': str(message.sender.id),
                    'sender_name': message.sender.get_full_name() or message.sender.email,
                    'sender_role': 'admin' if message.sender.is_staff else 'customer',
                    'timestamp': message.timestamp.isoformat(),
                    'is_read': message.is_read,
                    'room_id': message.chat_room.id,
                    'room_name': chat_room.community.name if chat_room.chat_type == ChatRoom.COMMUNITY else chat_room.subject,
                    'message_type': message.message_type,
                    'image_url': file_url,
                    'source': 'mobile'
                }
            )

            return Response({
                'message_id': message.id,
                'image_url': file_url
            }, status=status.HTTP_201_CREATED)

        except ChatRoom.DoesNotExist:
            return Response(
                {'error': 'Chat room not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Image upload error: {str(e)}")
            return Response(
                {'error': 'Failed to upload image'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MobileMarkMessagesAsReadView(APIView):
    permission_classes = [JWTAuthentication]

    def post(self, request, room_id):
        try:
            chat_room = ChatRoom.objects.get(id=room_id)
            if chat_room.chat_type == ChatRoom.COMMUNITY:
                if not chat_room.members.filter(id=request.user.id).exists():
                    return Response(
                        {'error': 'Not authorized to access this room'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            elif not (request.user == chat_room.customer or request.user == chat_room.admin):
                return Response(
                    {'error': 'Not authorized to access this room'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Mark messages as read
            Message.objects.filter(
                chat_room=chat_room,
                is_read=False
            ).exclude(
                sender=request.user
            ).update(is_read=True)

            # Clear notifications
            ChatNotification.objects.filter(
                user=request.user,
                chat_room=chat_room
            ).update(count=0)

            return Response({'status': 'success'})

        except ChatRoom.DoesNotExist:
            return Response(
                {'error': 'Chat room not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Mark messages as read error: {str(e)}")
            return Response(
                {'error': 'Failed to mark messages as read'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
