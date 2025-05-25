import json
import jwt
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from chat.models import ChatRoom, Message, ChatNotification
from django.db.models import Q
from backend.models import CustomUser
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class MobileChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            # Get token from URL parameters
            token = self.scope['url_route']['kwargs'].get('token')
            if not token:
                await self.close(code=4001)
                return

            # Verify JWT token and get user
            self.user = await self.get_user_from_token(token)
            if not self.user:
                await self.close(code=4001)
                return

            # Create both mobile and web group names for the user
            self.mobile_group_name = f'user_{self.user.id}_mobile'
            self.web_group_name = f'user_{self.user.id}_web'
            
            # Join user's mobile group
            await self.channel_layer.group_add(
                self.mobile_group_name,
                self.channel_name
            )
            
            await self.accept()
            await self.join_room_groups()
            
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': 'Connected to mobile chat'
            }))
            
        except Exception as e:
            logger.error(f"Mobile connection error: {str(e)}")
            await self.close(code=4000)

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.mobile_group_name,
                self.channel_name
            )
            await self.leave_room_groups()
        except Exception as e:
            logger.error(f"Mobile disconnection error: {str(e)}")

    async def receive(self, text_data=None, bytes_data=None):
        try:
            if bytes_data:
                # Handle binary data (image upload)
                await self.handle_image_upload(bytes_data)
                return

            if not text_data:
                raise ValueError("No data provided")
                
            data = json.loads(text_data)
            logger.debug(f"Received mobile WebSocket data: {data}")
            
            if data.get('type') == 'ping':
                await self.send(json.dumps({'type': 'pong'}))
                return

            if data.get('type') == 'typing':
                room_id = data.get('room_id')
                if room_id:
                    # Broadcast typing to both mobile and web groups
                    await self.channel_layer.group_send(
                        f'chat_{room_id}',
                        {
                            'type': 'typing_message',
                            'is_typing': data.get('is_typing', False),
                            'sender_id': str(self.user.id),
                            'room_id': room_id,
                            'source': 'mobile'
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

            if data.get('type') == 'image':
                try:
                    logger.debug("Starting to process image message...")
                    room_id = data.get('room_id')
                    image_url = data.get('image_url')
                    content = data.get('content', 'Image shared')
                    
                    logger.debug(f"Image message data - Room ID: {room_id}, Image URL: {image_url}, Content: {content}")
                    logger.debug(f"Current user: {self.user.id}, is_staff: {self.user.is_staff}")
                    
                    if not room_id:
                        raise ValueError("Room ID is required")
                    if not image_url:
                        raise ValueError("Image URL is required")
                    
                    # Verify room exists and user has access
                    room = await self.verify_room_access(room_id)
                    logger.debug(f"Room verified: {room.id}, type: {room.chat_type}")
                    
                    # Create message
                    message_obj = await self.save_image_message(room_id, image_url)
                    logger.debug(f"Image message created with ID: {message_obj.id}")
                    
                    room_name = await self.get_room_name(room_id)
                    logger.debug(f"Room name retrieved: {room_name}")
                    
                    # Prepare message data
                    message_data = {
                        'type': 'chat_message',
                        'id': str(message_obj.id),
                        'message': content,
                        'sender_id': str(self.user.id),
                        'sender_name': await self.get_user_display_name(self.user),
                        'sender_role': 'admin' if self.user.is_staff else 'customer',
                        'timestamp': message_obj.timestamp.isoformat(),
                        'is_read': message_obj.is_read,
                        'room_id': room_id,
                        'room_name': room_name or 'Support',
                        'message_type': 'image',
                        'image_url': image_url,
                        'source': 'mobile'
                    }
                    
                    logger.debug(f"Broadcasting image message: {message_data}")
                    
                    # 1. Echo to sender
                    await self.send(text_data=json.dumps(message_data))
                    # 2. Broadcast to both mobile and web groups
                    await self.channel_layer.group_send(
                        f'chat_{room_id}',
                        message_data
                    )
                    
                except Exception as e:
                    logger.error(f"Error processing image message: {str(e)}", exc_info=True)
                    await self.send_error(f"Failed to process image message: {str(e)}")
                return

            if data.get('type') == 'chat':
                message = data.get('message', '').strip()
                room_id = data.get('room_id')
                if message and room_id:
                    message_obj = await self.save_message(message, room_id)
                    room_name = await self.get_room_name(room_id)
                    
                    # Prepare message data
                    message_data = {
                        'type': 'chat_message',
                        'id': str(message_obj.id),
                        'message': message_obj.content,
                        'sender_id': str(self.user.id),
                        'sender_name': await self.get_user_display_name(self.user),
                        'sender_role': 'admin' if self.user.is_staff else 'customer',
                        'timestamp': message_obj.timestamp.isoformat(),
                        'is_read': message_obj.is_read,
                        'room_id': room_id,
                        'room_name': room_name or 'Support',
                        'message_type': message_obj.message_type,
                        'source': 'mobile'
                    }
                    # 1. Echo to sender
                    await self.send(text_data=json.dumps(message_data))
                    # 2. Broadcast to both mobile and web groups
                    await self.channel_layer.group_send(
                        f'chat_{room_id}',
                        message_data
                    )

        except json.JSONDecodeError:
            logger.error("Invalid JSON format received", exc_info=True)
            await self.send_error('Invalid JSON format')
        except ValueError as e:
            logger.error(f"Value error: {str(e)}", exc_info=True)
            await self.send_error(str(e))
        except Exception as e:
            logger.error(f"Mobile receive error: {str(e)}", exc_info=True)
            await self.send_error('Internal server error')

    async def handle_image_upload(self, bytes_data):
        try:
            # First 4 bytes contain the room_id as a 32-bit integer
            room_id = int.from_bytes(bytes_data[:4], byteorder='big')
            
            # Next 4 bytes contain the image size
            image_size = int.from_bytes(bytes_data[4:8], byteorder='big')
            
            # Remaining bytes are the image data
            image_data = bytes_data[8:8+image_size]
            
            # Save image
            file_name = f"chat_images/{room_id}/{timezone.now().timestamp()}.jpg"
            file_path = default_storage.save(file_name, ContentFile(image_data))
            file_url = default_storage.url(file_path)

            # Create message
            message_obj = await self.save_image_message(room_id, file_url)
            room_name = await self.get_room_name(room_id)

            # Prepare message data
            message_data = {
                'type': 'chat_message',
                'id': str(message_obj.id),
                'message': 'Image shared',
                'sender_id': str(self.user.id),
                'sender_name': await self.get_user_display_name(self.user),
                'sender_role': 'admin' if self.user.is_staff else 'customer',
                'timestamp': message_obj.timestamp.isoformat(),
                'is_read': message_obj.is_read,
                'room_id': room_id,
                'room_name': room_name or 'Support',
                'message_type': 'image',
                'image_url': file_url,
                'source': 'mobile'
            }

            # Broadcast to both mobile and web groups
            await self.channel_layer.group_send(
                f'chat_{room_id}',
                message_data
            )

        except Exception as e:
            logger.error(f"Image upload error: {str(e)}")
            await self.send_error('Failed to upload image')

    async def chat_message(self, event):
        # Process messages from both web and mobile
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'id': event['id'],
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'sender_role': event['sender_role'],
            'timestamp': event['timestamp'],
            'is_read': event['is_read'],
            'room_id': event['room_id'],
            'room_name': event['room_name'],
            'message_type': event['message_type'],
            'image_url': event.get('image_url')
        }))

    async def typing_message(self, event):
        # Process typing events from both web and mobile
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'is_typing': event['is_typing'],
            'sender_id': event['sender_id'],
            'room_id': event['room_id']
        }))

    async def send_error(self, error):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'error': error
        }))

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            if user_id:
                return CustomUser.objects.get(id=user_id)
        except (jwt.InvalidTokenError, CustomUser.DoesNotExist):
            return None
        return None

    @database_sync_to_async
    def get_rooms_for_user(self):
        return list(ChatRoom.objects.filter(
            Q(customer=self.user) | Q(admin=self.user) | Q(members=self.user)
        ))

    async def join_room_groups(self):
        rooms = await self.get_rooms_for_user()
        for room in rooms:
            # Join both mobile and web groups for each room
            await self.channel_layer.group_add(
                f'chat_{room.id}',
                self.channel_name
            )

    async def leave_room_groups(self):
        rooms = await self.get_rooms_for_user()
        for room in rooms:
            await self.channel_layer.group_discard(
                f'chat_{room.id}',
                self.channel_name
            )

    @database_sync_to_async
    def save_message(self, message, room_id):
        room = ChatRoom.objects.get(id=room_id)
        if room.chat_type == ChatRoom.COMMUNITY:
            if not room.members.filter(id=self.user.id).exists():
                raise ValueError("User is not a member of this community")
        message_obj = Message.objects.create(
            chat_room=room,
            sender=self.user,
            content=message
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
    def verify_room_access(self, room_id):
        try:
            room = ChatRoom.objects.get(id=room_id)
            if room.chat_type == ChatRoom.COMMUNITY:
                if not room.members.filter(id=self.user.id).exists():
                    raise ValueError("User is not a member of this community")
            elif self.user != room.customer and self.user != room.admin:
                raise ValueError("User does not have access to this chat room")
            return room
        except ChatRoom.DoesNotExist:
            raise ValueError(f"Chat room {room_id} does not exist")
        except Exception as e:
            logger.error(f"Error verifying room access: {str(e)}", exc_info=True)
            raise

    @database_sync_to_async
    def save_image_message(self, room_id, image_url):
        try:
            logger.debug(f"Saving image message - Room ID: {room_id}, Image URL: {image_url}")
            
            room = ChatRoom.objects.get(id=room_id)
            if room.chat_type == ChatRoom.COMMUNITY:
                if not room.members.filter(id=self.user.id).exists():
                    raise ValueError("User is not a member of this community")
            
            # Create the message
            message_obj = Message.objects.create(
                chat_room=room,
                sender=self.user,
                content='Image shared',
                message_type='image',
                image=image_url
            )
            logger.debug(f"Message created with ID: {message_obj.id}")
            
            # Update room timestamp
            room.update_timestamp()
            
            # Create notifications
            if room.chat_type == ChatRoom.COMMUNITY:
                for member in room.members.exclude(id=self.user.id):
                    notification, created = ChatNotification.objects.get_or_create(
                        user=member,
                        chat_room=room,
                        defaults={'count': 1}
                    )
                    if not created:
                        notification.increment()
                    logger.debug(f"Notification created/updated for member {member.id}")
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
                    logger.debug(f"Notification created/updated for recipient {recipient.id}")
            
            return message_obj
            
        except ChatRoom.DoesNotExist:
            logger.error(f"Chat room not found: {room_id}", exc_info=True)
            raise ValueError("Chat room not found")
        except Exception as e:
            logger.error(f"Error saving image message: {str(e)}", exc_info=True)
            raise

    @database_sync_to_async
    def get_room_name(self, room_id):
        try:
            room = ChatRoom.objects.get(id=room_id)
            if room.chat_type == ChatRoom.COMMUNITY:
                return room.community.name if room.community else 'Community Chat'
            return room.subject
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def get_user_display_name(self, user):
        if not user:
            return "System"
        return user.get_full_name() or user.email 