from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message, ChatNotification
from .serializers import ChatRoomSerializer, MessageSerializer, ChatNotificationSerializer
from django.db.models import Q, Max
from django.utils import timezone
from backend.models import PostCommunity, PostCommunityJoiners
import uuid
import logging
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from datetime import datetime
import os
from backend.models import CustomUser
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

class CommunityChatRoomListView(generics.ListAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            user = self.request.user
            logger.info(f"Fetching community rooms for user: {user.email}")
            
            if not user.is_authenticated:
                logger.warning("User is not authenticated")
                return ChatRoom.objects.none()

            # If user is admin, return all community chat rooms
            if user.is_staff:
                queryset = ChatRoom.objects.filter(
                    chat_type=ChatRoom.COMMUNITY
                ).order_by('-updated_at')
                logger.info(f"Admin user - returning all community chat rooms: {queryset.count()}")
                return queryset
                
            # For regular users, fetch rooms where user is a member
            queryset = ChatRoom.objects.filter(
                chat_type=ChatRoom.COMMUNITY,
                members=user
            ).order_by('-updated_at')
            logger.info(f"Regular user - chat rooms found: {queryset.count()}")
            
            for room in queryset:
                logger.debug(f"Room: {room.room_name}, Community: {room.community.name}")
                
            return queryset
        except Exception as e:
            logger.error(f"Error in CommunityChatRoomListView: {str(e)}", exc_info=True)
            raise

class CommunityChatRoomCreateView(generics.CreateAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            user = request.user
            community = PostCommunity.objects.first()
            if not community:
                return Response(
                    {'error': 'No community exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            if not PostCommunityJoiners.objects.filter(
                user=user,
                is_active=True
            ).exists():
                return Response(
                    {'error': 'User is not an active member of the community'},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            room_name = f"community_chat_{uuid.uuid4().hex}"
            chat_room = ChatRoom.objects.create(
                room_name=room_name,
                chat_type=ChatRoom.COMMUNITY,
                community=community,
                is_active=True
            )
            
            # Add all community members to the chat room
            community_members = PostCommunityJoiners.objects.filter(
                community=community,
                is_active=True
            ).values_list('user', flat=True)
            chat_room.members.add(*community_members)
            
            serializer = self.get_serializer(chat_room)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating community chatroom: {str(e)}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class ChatRoomListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(
            (
                Q(customer=user) | Q(admin=user) | Q(members=user)) & ~Q(customer=None)  ).annotate(
            last_message_time=Max('messages__timestamp')
        ).order_by('-last_message_time', '-updated_at')

    def create(self, request, *args, **kwargs):
        try:
            customer = request.user
            admin = CustomUser.objects.filter(is_staff=True).first()
            subject = request.data.get('subject', 'General Inquiry')
            
            room_name = f"chat_{uuid.uuid4().hex}"
            chat_room = ChatRoom.objects.create(
                customer=customer,
                admin=admin,
                room_name=room_name,
                subject=subject,
                is_active=True
            )
            
            serializer = self.get_serializer(chat_room)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class ImageUploadView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            print("Saving image file .....")
            image_file = request.FILES.get('image')
            room_id = request.POST.get('room_id')
            
            if not image_file or not room_id:
                return Response(
                    {'error': 'Image and room_id are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            chat_room = ChatRoom.objects.get(id=room_id)
            if chat_room.chat_type == ChatRoom.COMMUNITY:
                if not chat_room.members.filter(id=request.user.id).exists():
                    return Response(
                        {'error': 'User is not a member of this community'},
                        status=status.HTTP_403_FORBIDDEN
                    )

            ext = os.path.splitext(image_file.name)[1]
            filename = f"chat_images/{uuid.uuid4()}{ext}"
            
            file_path = default_storage.save(filename, ContentFile(image_file.read()))
            file_url = f"/{file_path}"

            # Set unread_by for image message
            if chat_room.chat_type == ChatRoom.COMMUNITY:
                unread_by = list(chat_room.members.exclude(id=request.user.id).values_list('id', flat=True))
            else:
                if request.user == chat_room.customer:
                    unread_by = [chat_room.admin.id] if chat_room.admin else []
                else:
                    unread_by = [chat_room.customer.id] if chat_room.customer else []

            message = Message.objects.create(
                sender=request.user,
                chat_room=chat_room,
                content='Image shared',
                message_type='image',
                image=file_url,
                unread_by=unread_by
            )
            
            chat_room.update_timestamp()
            
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
            print(f"[WebSocket] Broadcasting message to group chat_{room_id} with message id {message.id}")
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
                    'unread_by': list(message.unread_by),  # send unread_by as list of user ids
                    'room_id': message.chat_room.id,
                    'room_name': chat_room.community.name if chat_room.chat_type == ChatRoom.COMMUNITY else chat_room.subject,
                    'message_type': message.message_type,
                    'image_url': file_url
                }
            )
            
            return Response({
                'image_url': file_url,
                'message_id': message.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        chat_room = ChatRoom.objects.get(id=room_id)
        if chat_room.chat_type == ChatRoom.COMMUNITY:
            # Allow admin users to access all community chat rooms
            if not self.request.user.is_staff and not chat_room.members.filter(id=self.request.user.id).exists():
                return Message.objects.none()
        return Message.objects.filter(
            chat_room_id=room_id
        ).select_related('sender').order_by('timestamp')

    def perform_create(self, serializer):
        room_id = self.kwargs['room_id']
        chat_room = ChatRoom.objects.get(id=room_id)
        if chat_room.chat_type == ChatRoom.COMMUNITY:
            if not self.request.user.is_staff and not chat_room.members.filter(id=self.request.user.id).exists():
                raise ValueError("User is not a member of this community")
            # All members except sender
            unread_by = list(chat_room.members.exclude(id=self.request.user.id).values_list('id', flat=True))
        else:
            # Private chat: the other participant
            if self.request.user == chat_room.customer:
                unread_by = [chat_room.admin.id] if chat_room.admin else []
            else:
                unread_by = [chat_room.customer.id] if chat_room.customer else []
        message = serializer.save(
            sender=self.request.user, 
            chat_room=chat_room,
            unread_by=unread_by
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

class UnreadMessagesView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        chat_room = ChatRoom.objects.get(id=room_id)
        if chat_room.chat_type == ChatRoom.COMMUNITY:
            # Allow admin users to access all community chat rooms
            if not self.request.user.is_staff and not chat_room.members.filter(id=self.request.user.id).exists():
                return Message.objects.none()
        # Only messages where the current user is in unread_by
        return Message.objects.filter(
            chat_room_id=room_id,
            unread_by__contains=[str(self.request.user.id)]
        ).exclude(sender=self.request.user)

class MarkMessagesAsReadView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        room_id = kwargs['room_id']
        chat_room = ChatRoom.objects.get(id=room_id)
        if chat_room.chat_type == ChatRoom.COMMUNITY:
            if not request.user.is_staff and not chat_room.members.filter(id=request.user.id).exists():
                return Response(
                    {'error': 'User is not a member of this community'},
                    status=status.HTTP_403_FORBIDDEN
                )
        # Find all messages in this room where the user is in unread_by and is not the sender
        messages = Message.objects.filter(
            chat_room_id=room_id,
            unread_by__contains=[str(request.user.id)]
        ).exclude(sender=request.user)
        # Remove user from unread_by for each message
        for msg in messages:
            msg.mark_as_read(str(request.user.id))
        # Reset notification count
        ChatNotification.objects.filter(
            user=request.user,
            chat_room_id=room_id
        ).update(count=0)
        return Response({'status': 'messages marked as read'})

class ChatNotificationListView(generics.ListAPIView):
    serializer_class = ChatNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatNotification.objects.filter(
            user=self.request.user,
            count__gt=0
        ).select_related('chat_room')