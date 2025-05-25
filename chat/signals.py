from django.db.models.signals import post_save
from django.dispatch import receiver
from backend.models import PostCommunity, PostCommunityJoiners
from .models import ChatRoom, Message

@receiver(post_save, sender=PostCommunity)
def create_community_chatroom(sender, instance, created, **kwargs):
    if created:
        ChatRoom.objects.create(
            chat_type=ChatRoom.COMMUNITY,
            community=instance,
            room_name=f"community_{instance.id}",
            subject=f"Community: {instance.name}"
        )

@receiver(post_save, sender=PostCommunityJoiners)
def notify_community_joiner(sender, instance, created, **kwargs):
    if created:
        chat_room = ChatRoom.objects.filter(community=instance.community).first()
        if chat_room:
            Message.objects.create(
                chat_room=chat_room,
                message_type=Message.SYSTEM,
                content=f"{instance.user.get_full_name()} has joined the community"
            )