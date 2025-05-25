# from django.db import models
# from django.utils import timezone
# from django.contrib.auth import get_user_model
# from django.core.exceptions import ValidationError
# from django.core.files.images import get_image_dimensions
# from backend.models import CustomUser

# def validate_image_size(image):
#     """Validate image dimensions and size."""
#     max_size_mb = 5
#     max_width = 1920
#     max_height = 1920
    
#     if image.size > max_size_mb * 1024 * 1024:
#         raise ValidationError(f"Image size should not exceed {max_size_mb}MB")
    
#     width, height = get_image_dimensions(image)
#     if width > max_width or height > max_height:
#         raise ValidationError(f"Image dimensions should not exceed {max_width}x{max_height}")

# class ChatRoom(models.Model):
#     COMMUNITY = 'community'
#     PRIVATE = 'private'
#     CHAT_TYPE_CHOICES = [
#         (COMMUNITY, 'Community Chat'),
#         (PRIVATE, 'Private Chat'),
#     ]
    
#     chat_type = models.CharField(max_length=10, choices=CHAT_TYPE_CHOICES, default=PRIVATE)
#     customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='customer_chatrooms', null=True, blank=True)
#     admin = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_chatrooms')
#     community = models.ForeignKey('backend.PostCommunity', on_delete=models.CASCADE, null=True, blank=True, related_name='chat_rooms')
#     members = models.ManyToManyField(CustomUser, related_name='community_chatrooms', blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     is_active = models.BooleanField(default=True)
#     subject = models.CharField(max_length=255, default='reservation')
#     room_name = models.CharField(max_length=255, unique=True)
    
#     class Meta:
#         ordering = ['-updated_at']
#         indexes = [
#             models.Index(fields=['customer', 'admin']),
#             models.Index(fields=['is_active']),
#             models.Index(fields=['chat_type']),
#         ]
    
#     def __str__(self):
#         if self.chat_type == self.COMMUNITY:
#             return f"Community Chat: {self.community.name if self.community else 'Unknown'}"
#         return f"Chat between {self.customer} and {self.admin or 'unassigned admin'}"
    
#     def update_timestamp(self):
#         """Update the updated_at field."""
#         self.updated_at = timezone.now()
#         self.save(update_fields=['updated_at'])

# class Message(models.Model):
#     TEXT = 'text'
#     IMAGE = 'image'
#     SYSTEM = 'system'
#     MESSAGE_TYPE_CHOICES = [
#         (TEXT, 'Text'),
#         (IMAGE, 'Image'),
#         (SYSTEM, 'System'),
#     ]
    
#     chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
#     sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
#     content = models.TextField()
#     message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, default=TEXT)
#     image = models.ImageField(upload_to='chat_images/', null=True, blank=True, validators=[validate_image_size])
#     timestamp = models.DateTimeField(auto_now_add=True)
#     is_read = models.BooleanField(default=False)
    
#     class Meta:
#         ordering = ['timestamp']
#         indexes = [
#             models.Index(fields=['chat_room', 'is_read']),
#             models.Index(fields=['timestamp']),
#             models.Index(fields=['message_type']),
#         ]
    
#     def __str__(self):
#         if self.message_type == self.SYSTEM:
#             return f"System message: {self.content}"
#         return f"Message from {self.sender} at {self.timestamp}"
    
#     def mark_as_read(self):
#         """Mark message as read."""
#         if not self.is_read:
#             self.is_read = True
#             self.save(update_fields=['is_read'])

# class ChatNotification(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
#     count = models.PositiveIntegerField(default=0)
#     last_updated = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         unique_together = ('user', 'chat_room')
#         indexes = [
#             models.Index(fields=['user', 'chat_room']),
#         ]
    
#     def __str__(self):
#         return f"{self.count} unread for {self.user}"
    
#     def increment(self):
#         """Increment unread count."""
#         self.count += 1
#         self.save(update_fields=['count', 'last_updated'])
    
#     def reset(self):
#         """Reset unread count to zero."""
#         if self.count > 0:
#             self.count = 0
#             self.save(update_fields=['count', 'last_updated'])