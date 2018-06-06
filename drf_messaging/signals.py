from django.db.models.signals import post_save
from django.dispatch import receiver

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Messages
from .utils import get_user_info_from_instance
from fcm_django.models import FCMDevice


@receiver(post_save, sender=Messages)
def send_message_to_socket(sender, instance, created, **kwargs):
    if created and hasattr(instance, 'receiver'):
        channel_layer = get_channel_layer()
        message = instance.message
        if getattr(instance.receiver, "info", None) and instance.receiver.info.current_channel:
            channel_name = instance.receiver.info.current_channel
            async_to_sync(channel_layer.send)(channel_name, {"type": "chat.message", "source": "signals",
                                                             "message": message,
                                                             "receiver": "you", "sender": instance.sender.id})
        if getattr(instance.sender, "info", None) and instance.sender.info.current_channel:
            channel_name = instance.sender.info.current_channel
            async_to_sync(channel_layer.send)(channel_name, {"type": "chat.message", "source": "signals",
                                                             "message": message,
                                                             "receiver": instance.receiver.id, "sender": "you"})
        fcm_devices = FCMDevice.objects.filter(user=instance.receiver)
        if fcm_devices:
            data = {
                "message": {
                    "sender": get_user_info_from_instance(instance.sender),
                    "message": message
                }
            }
            new_messages = Messages.objects.get_unread(instance.receiver)
            data['new_messages'] = [{
                "sender": get_user_info_from_instance(instance.sender),
                "count": message.get('count')
            } for message in new_messages]

            fcm_devices.send_message(data=data)
