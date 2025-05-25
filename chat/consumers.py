import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message, ChatNotification
from django.db.models import Q
from backend.models import PostCommunityJoiners
from io import BytesIO
from PIL import Image
from django.core.files.images import ImageFile
from django.conf import settings
import logging
from datetime import datetime
from backend.models import CustomUser

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_id = self.scope['url_route']['kwargs']['room_id']
            self.room_group_name = f'chat_{self.room_id}'
            self.user = self.scope["user"]
            
            if not self.user.is_authenticated:
                await self.close(code=4001)
                return

            if not await self.verify_room_access():
                await self.close(code=4003)
                return

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': 'Connected to chat room'
            }))
            
            # Send all historical messages for community chat
            if await self.is_community_room():
                messages = await self.get_all_messages()
                for message in messages:
                    await self.send(text_data=json.dumps(message))
                    
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            await self.close(code=4000)

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            logger.error(f"Disconnection error: {str(e)}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            
            if data.get('type') == 'image':
                room_id = data['room_id']
                room = await self.get_room(room_id)
                
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': {
                            'type': 'image',
                            'sender_id': self.user.id,
                            'sender_name': self.user.get_full_name(),
                            'room_id': room_id,
                            'image_url': data['image_url'],
                            'content': data.get('content', ''),
                            'timestamp': str(datetime.now()),
                        },
                        'source': 'web'
                    }
                )
            elif data.get('type') == 'message':
                message = data.get('message', '').strip()
                room_id = data.get('room_id')
                if message and room_id:
                    message_obj = await self.save_message(message, room_id)
                    await self.broadcast_message(message_obj)
                    
        except Exception as e:
            logger.error(f"WebSocket error: {str(e)}")

    @database_sync_to_async
    def save_image_message(self, image_data, room_id, filename):
        room = ChatRoom.objects.get(id=room_id)
        if room.chat_type == ChatRoom.COMMUNITY:
            if not room.members.filter(id=self.user.id).exists():
                raise ValueError("User is not a member of this community")
        
        img = Image.open(BytesIO(image_data))
        if img.format not in ['JPEG', 'PNG']:
            img = img.convert('RGB')
        
        img_io = BytesIO()
        img.save(img_io, format='JPEG', quality=85, optimize=True)
        img.close()
        
        message = Message.objects.create(
            chat_room=room,
            sender=self.user,
            message_type=Message.IMAGE,
            content="[Image]"
        )
        
        filename = f"chat_{room_id}_{uuid.uuid4().hex[:8]}_{filename}"
        message.image.save(filename, ImageFile(img_io), save=True)
        
        room.update_timestamp()
        
        if room.chat_type == ChatRoom.COMMUNITY:
            for member in room.members.exclude(id=self.user.id):
                notification, created = ChatNotification.objects.get_or_create(
                    user=member,
                    chat_room=room,
                    defaults={'count': 1}
                )
                if not created:
                    notification.increment()
        else:
            recipient = room.admin if self.user == room.customer else room.customer
            if recipient:
                notification, created = ChatNotification.objects.get_or_create(
                    user=recipient,
                    chat_room=room,
                    defaults={'count': 1}
                )
                if not created:
                    notification.increment()
        
        return message

    async def broadcast_message(self, message_obj):
        try:
            logger.info(f"Broadcasting message {message_obj.id} to group {self.room_group_name}")
            message_data = {
                'type': 'chat',
                'id': str(message_obj.id),
                'message': message_obj.content,
                'sender_id': str(message_obj.sender.id) if message_obj.sender else None,
                'sender_name': await self.get_user_display_name(message_obj.sender) if message_obj.sender else "System",
                'sender_role': 'admin' if message_obj.sender and message_obj.sender.is_staff else 'customer',
                'timestamp': message_obj.timestamp.isoformat(),
                'unread_by': list(message_obj.unread_by),  # Use string UUID for is_read
                'room_id': message_obj.chat_room.id,
                'room_name': await self.get_room_name(message_obj.chat_room.id) or 'Support',
                'message_type': message_obj.message_type,
                'source': 'web'
            }
            
            if message_obj.message_type == Message.IMAGE and message_obj.image:
                message_data['image_url'] = await self.get_image_url(message_obj)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    **message_data
                }
            )
            logger.info(f"Message {message_obj.id} sent to group {self.room_group_name}")
        except Exception as e:
            logger.error(f"Broadcast message error: {str(e)}", exc_info=True)

    @database_sync_to_async
    def get_image_url(self, message_obj):
        if message_obj.image and hasattr(message_obj.image, 'url'):
            return f"{settings.MEDIA_URL}{message_obj.image.name}"
        return None

    async def send_error(self, error):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'error': error
        }))

    @database_sync_to_async
    def verify_room_access(self):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            if room.chat_type == ChatRoom.COMMUNITY:
                # Allow admin users to access all community chat rooms
                return self.user.is_staff or room.members.filter(id=self.user.id).exists()
            return True
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def is_community_room(self):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            return room.chat_type == ChatRoom.COMMUNITY
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def get_all_messages(self):
        messages = Message.objects.filter(chat_room_id=self.room_id).select_related('sender').order_by('timestamp')
        return [{
            'type': 'chat',
            'id': str(msg.id),
            'message': msg.content,
            'sender_id': str(msg.sender.id) if msg.sender else None,
            'sender_name': msg.sender.get_full_name() or msg.sender.email if msg.sender else "System",
            'sender_role': 'admin' if msg.sender and msg.sender.is_staff else 'customer',
            'timestamp': msg.timestamp.isoformat(),
            'unread_by': list(msg.unread_by),  # Use string UUID for is_read
            'room_id': msg.chat_room.id,
            'room_name': msg.chat_room.community.name if msg.chat_room.chat_type == ChatRoom.COMMUNITY else msg.chat_room.subject,
            'message_type': msg.message_type,
            'image_url': f"{settings.MEDIA_URL}{msg.image.name}" if msg.message_type == Message.IMAGE and msg.image else None
        } for msg in messages]

    @database_sync_to_async
    def save_message(self, message, room_id):
        try:
            room = ChatRoom.objects.get(id=room_id)
            if room.chat_type == ChatRoom.COMMUNITY:
                if not self.user.is_staff and not room.members.filter(id=self.user.id).exists():
                    raise ValueError("User is not a member of this community")
                unread_by = [str(member.id) for member in room.members.exclude(id=self.user.id)]
            else:
                if self.user == room.customer and room.admin:
                    unread_by = [str(room.admin.id)]
                elif self.user == room.admin and room.customer:
                    unread_by = [str(room.customer.id)]
                else:
                    unread_by = []
            message_obj = Message.objects.create(
                chat_room=room,
                sender=self.user,
                content=message,
                unread_by=unread_by
            )
            room.update_timestamp()
            if room.chat_type == ChatRoom.COMMUNITY:
                for member in room.members.exclude(id=self.user.id):
                    notification, created = ChatNotification.objects.get_or_create(
                        user=member,
                        chat_room=room,
                        defaults={'count': 1}
                    )
                    if not created:
                        notification.increment()
            else:
                recipient = room.admin if self.user == room.customer else room.customer
                if recipient:
                    notification, created = ChatNotification.objects.get_or_create(
                        user=recipient,
                        chat_room=room,
                        defaults={'count': 1}
                    )
                    if not created:
                        notification.increment()
            return message_obj
        except Exception as e:
            logger.error(f"Error in save_message: {str(e)}", exc_info=True)
            raise

    @database_sync_to_async
    def get_user_display_name(self, user):
        return user.get_full_name() or user.email

    @database_sync_to_async
    def get_room_name(self, room_id):
        room = ChatRoom.objects.get(id=room_id)
        if room.chat_type == ChatRoom.COMMUNITY:
            return room.community.name
        if self.user.is_staff:
            return f"{room.customer.get_full_name() or room.customer.email} - {room.subject}"
        return room.subject

    async def chat_message(self, event):
        logger.info(f"Sending chat_message event to frontend: {event}")
        message_data = {
            'type': 'chat',
            'id': event['id'],
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'sender_role': event['sender_role'],
            'timestamp': event['timestamp'],
            'unread_by': event['unread_by'],
            'room_id': event['room_id'],
            'room_name': event['room_name'],
            'message_type': event['message_type']
        }
        
        # Add image_url if present
        if event.get('image_url'):
            message_data['image_url'] = event['image_url']
        # Defensive: ensure all required fields are present
        required_fields = ['id', 'message', 'sender_id', 'sender_name', 'sender_role', 'timestamp', 'unread_by', 'room_id', 'room_name', 'message_type']
        for field in required_fields:
            if field not in message_data:
                logger.error(f"Missing field in chat_message event: {field}. Event: {event}")
                message_data[field] = None
        await self.send(text_data=json.dumps(message_data))

    async def typing_message(self, event):
        # Only process typing events from mobile if we're in web consumer
        if event.get('source') == 'mobile':
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'is_typing': event['is_typing'],
                'sender_id': event['sender_id'],
                'room_id': event['room_id']
            }))

class GlobalChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.user = self.scope["user"]
            self.group_name = f'user_{self.user.id}_global'

            if not self.user.is_authenticated:
                await self.close(code=4001)
                return

            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
            await self.join_room_groups()
        except Exception as e:
            logger.error(f"Global connection error: {str(e)}")
            await self.close(code=4000)

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            await self.leave_room_groups()
        except Exception as e:
            logger.error(f"Global disconnection error: {str(e)}")

    async def receive(self, text_data=None, bytes_data=None):
        try:
            if bytes_data:
                await self.send_error('Image uploads not supported on global WebSocket')
                return
                
            if not text_data:
                raise ValueError("No data provided")
                
            data = json.loads(text_data)
            logger.debug(f"Received WebSocket data: {data}")
            
            if data.get('type') == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
                return

            if data.get('type') == 'typing':
                room_id = data.get('room_id')
                if room_id:
                    await self.channel_layer.group_send(
                        f'chat_{room_id}',
                        {
                            'type': 'typing_message',
                            'is_typing': data.get('is_typing', False),
                            'sender_id': str(self.user.id),
                            'room_id': room_id
                        }
                    )
                return

            if data.get('type') == 'join':
                room_id = data.get('room_id')
                if room_id:
                    await self.channel_layer.group_add(
                        f'chat_{room_id}',
                        self.channel_name
                    )
                return

            if data.get('type') == 'chat':
                message = data.get('message', '').strip()
                room_id = data.get('room_id')
                
                if not message or not room_id:
                    await self.send_error('Message and room_id are required')
                    return
                    
                try:
                    # Step 1: Save the message
                    logger.debug(f"Attempting to save message in room {room_id}")
                    message_obj = await self.save_message(message, room_id)
                    logger.debug(f"Message saved successfully with ID {message_obj.id}")

                    # Step 2: Get room name
                    logger.debug(f"Getting room name for room {room_id}")
                    room_name = await self.get_room_name(room_id)
                    logger.debug(f"Room name retrieved: {room_name}")

                    # Step 3: Prepare message data
                    message_data = {
                        'type': 'chat_message',
                        'id': str(message_obj.id),
                        'message': message_obj.content,
                        'sender_id': str(self.user.id),
                        'sender_name': await self.get_user_display_name(self.user),
                        'sender_role': 'admin' if self.user.is_staff else 'customer',
                        'timestamp': message_obj.timestamp.isoformat(),
                        'unread_by': list(message_obj.unread_by),
                        'room_id': room_id,
                        'room_name': room_name or 'Support',
                        'message_type': message_obj.message_type
                    }
                    logger.debug(f"Prepared message data: {message_data}")

                    # Step 4: Broadcast to chat room
                    logger.debug(f"Broadcasting message to chat_{room_id}")
                    await self.channel_layer.group_send(
                        f'chat_{room_id}',
                        message_data
                    )
                    logger.debug("Message broadcast successful")

                    # Step 5: Send notifications
                    logger.debug("Preparing to send notifications")
                    # Get members who should receive notifications
                    member_ids = await self.get_room_member_ids(room_id)
                    logger.debug(f"Notification recipients: {member_ids}")

                    for uid in member_ids:
                        group_name = f'user_{uid}_global'
                        notification_data = {
                            'type': 'chat_notification',
                            'room_id': room_id,
                            'room_name': room_name or 'Support',
                            'message': message_obj.content,
                            'sender_id': str(self.user.id),
                            'sender_name': await self.get_user_display_name(self.user),
                            'timestamp': message_obj.timestamp.isoformat(),
                            'message_type': message_obj.message_type
                        }
                        logger.debug(f"Sending notification to {group_name}")
                        await self.channel_layer.group_send(
                            group_name,
                            notification_data
                        )
                    logger.debug("All notifications sent successfully")

                except Exception as e:
                    logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
                    # Try to send a more specific error message
                    error_message = f"Failed to process message: {str(e)}"
                    logger.error(error_message)
                    await self.send_error(error_message)
                    return

        except json.JSONDecodeError:
            logger.error("Invalid JSON format in WebSocket message")
            await self.send_error('Invalid JSON format')
        except ValueError as e:
            logger.error(f"Value error in WebSocket message: {str(e)}")
            await self.send_error(str(e))
        except Exception as e:
            logger.error(f"Unexpected error in WebSocket receive: {str(e)}", exc_info=True)
            await self.send_error('Internal server error')

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'id': event['id'],
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'sender_role': event['sender_role'],
            'timestamp': event['timestamp'],
            'unread_by': event['unread_by'],
            'room_id': event['room_id'],
            'room_name': event['room_name'],
            'message_type': event['message_type'],
            'image_url': event.get('image_url')
        }))

    async def typing_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'is_typing': event['is_typing'],
            'sender_id': event['sender_id'],
            'room_id': event['room_id']
        }))

    async def chat_notification(self, event):
        # Send notification to the user's global socket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'room_id': event['room_id'],
            'room_name': event['room_name'],
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'timestamp': event['timestamp'],
            'message_type': event['message_type']
        }))

    async def send_error(self, error):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'error': error
        }))

    @database_sync_to_async
    def get_user_rooms(self):
        return list(ChatRoom.objects.filter(
            Q(customer=self.user) | Q(admin=self.user) | Q(members=self.user)
        ))

    async def join_room_groups(self):
        rooms = await self.get_user_rooms()
        for room in rooms:
            await self.channel_layer.group_add(
                f'chat_{room.id}',
                self.channel_name
            )

    async def leave_room_groups(self):
        rooms = await self.get_user_rooms()
        for room in rooms:
            await self.channel_layer.group_discard(
                f'chat_{room.id}',
                self.channel_name
            )

    @database_sync_to_async
    def get_room_member_ids(self, room_id):
        room = ChatRoom.objects.get(id=room_id)
        member_ids = list(room.members.values_list('id', flat=True))
        
        if room.admin:
            member_ids.append(room.admin.id)
        if room.customer:
            member_ids.append(room.customer.id)
            
        # Convert to string and exclude the current user
        return [str(uid) for uid in member_ids if str(uid) != str(self.user.id)]

    @database_sync_to_async
    def save_message(self, message, room_id):
        try:
            room = ChatRoom.objects.get(id=room_id)
            if room.chat_type == ChatRoom.COMMUNITY:
                if not self.user.is_staff and not room.members.filter(id=self.user.id).exists():
                    raise ValueError("User is not a member of this community")
                unread_by = [str(member.id) for member in room.members.exclude(id=self.user.id)]
            else:
                if self.user == room.customer and room.admin:
                    unread_by = [str(room.admin.id)]
                elif self.user == room.admin and room.customer:
                    unread_by = [str(room.customer.id)]
                else:
                    unread_by = []
            message_obj = Message.objects.create(
                chat_room=room,
                sender=self.user,
                content=message,
                unread_by=unread_by
            )
            room.update_timestamp()
            if room.chat_type == ChatRoom.COMMUNITY:
                for member in room.members.exclude(id=self.user.id):
                    notification, created = ChatNotification.objects.get_or_create(
                        user=member,
                        chat_room=room,
                        defaults={'count': 1}
                    )
                    if not created:
                        notification.increment()
            else:
                recipient = room.admin if self.user == room.customer else room.customer
                if recipient:
                    notification, created = ChatNotification.objects.get_or_create(
                        user=recipient,
                        chat_room=room,
                        defaults={'count': 1}
                    )
                    if not created:
                        notification.increment()
            return message_obj
        except Exception as e:
            logger.error(f"Error in save_message: {str(e)}", exc_info=True)
            raise

    @database_sync_to_async
    def save_image_message(self, room_id, content, image_url):
        room = ChatRoom.objects.get(id=room_id)
        if room.chat_type == ChatRoom.COMMUNITY:
            # Allow admin users to send messages in community chat rooms
            if not self.user.is_staff and not room.members.filter(id=self.user.id).exists():
                raise ValueError("User is not a member of this community")
        message_obj = Message.objects.create(
            chat_room=room,
            sender=self.user,
            content=content,
            message_type=Message.IMAGE,
            image=image_url
        )
        room.update_timestamp()
        
        if room.chat_type == ChatRoom.COMMUNITY:
            for member in room.members.exclude(id=self.user.id):
                notification, created = ChatNotification.objects.get_or_create(
                    user=member,
                    chat_room=room,
                    defaults={'count': 1}
                )
                if not created:
                    notification.increment()
        else:
            recipient = room.admin if self.user == room.customer else room.customer
            if recipient:
                notification, created = ChatNotification.objects.get_or_create(
                    user=recipient,
                    chat_room=room,
                    defaults={'count': 1}
                )
                if not created:
                    notification.increment()
        return message_obj

    @database_sync_to_async
    def get_user_display_name(self, user):
        return user.get_full_name() or user.email

    @database_sync_to_async
    def get_room_name(self, room_id):
        room = ChatRoom.objects.get(id=room_id)
        if room.chat_type == ChatRoom.COMMUNITY:
            return room.community.name
        if self.user.is_staff:
            return f"{room.customer.get_full_name() or room.customer.email} - {room.subject}"
        return room.subject