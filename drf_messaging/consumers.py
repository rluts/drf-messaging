from django.conf import settings

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .exceptions import ClientError
from .models import Messages, UserTechInfo
from asgiref.sync import AsyncToSync
from .validators import blacklist_validator


# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class SocketCostumer(AsyncJsonWebsocketConsumer):

    # WebSocket event handlers

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat = None

    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        if self.scope["user"].is_anonymous:
            logger.debug("user anon")
            await self.close()
        else:
            logger.debug("user %s accepted" % self.scope["user"].username)
            await self.accept()
            await self.connect_user()

    async def receive_json(self, content):
        """
        Called when we get a text frame. Channels will JSON-decode the payload
        for us and pass it as the first argument.
        """
        # Messages will have a "command" key we can switch on
        command = content.get("command", None)
        try:
            if command == "join_chat":
                if content.get('user_id'):
                    try:
                        self.chat = User.objects.get(id=content.get('user_id')).id
                        await self.send_json({"chat": self.chat})
                    except User.DoesNotExist:
                        await self.send_json({"error": "USER_NOT_FOUND"})
                    except:
                        await self.send_json({"error": "BAD_REQUEST"})
            elif command == "leave_chat":
                self.chat = None
                await self.send_json({
                    "chat": self.chat
                })
            elif content.get('message'):
                await self.send_message(content.get('message'))
        except ClientError as e:
            # Catch any errors and send it back
            await self.send_json({"error": e.code})

    async def disconnect(self, code):
        """
        Called when the WebSocket closes for any reason.
        """
        await self.disconnect_user()

    async def connect_user(self):
        """
        Called when user connected to app
        """
        user = self.scope["user"]
        profile, created = UserTechInfo.objects.get_or_create(user=user)
        profile.current_channel = self.channel_name
        profile.online = True
        profile.save()
        await self.send_json(
            {
                "user": user.username,
            },
        )

    async def chat_message(self, event):
#        try:
            if event.get('source') == "signals":
                logger.debug(str(event))
                if event.get("sender") == "you" or (event.get('receiver') == 'you' and self.chat == event.get('sender')):
                    response = {
                        "message": event.get("message"),
                        "receiver": event.get("receiver"),
                        "sender": event.get("sender"),
                    }
                elif event.get('receiver') == "you":
                    # refresh new messages if chat not joined
                    new_messages = Messages.objects.get_unread(self.scope["user"].id)
                    response = {
                        "new_messages": [{
                            "sender": message.get('sender'),
                            "count": message.get('count')
                        } for message in new_messages]
                    }
                else:
                    return False
                await self.send_json(response)
#        except:
#            pass

    @database_sync_to_async
    def send_message(self, message):
        if not self.chat:
            AsyncToSync(self.send_json)(
                {
                    'error': 'NO_CHAT_JOINED'
                }
            )
        else:
            try:
                blacklist_validator(message)
                Messages.objects.send_message(sender=self.scope['user'], receiver_id=self.chat, message=message)
            except ValidationError:
                AsyncToSync(self.send_json)(
                    {
                        'error': 'BLACKLISTED_MESSAGE'
                    }
                )

    @database_sync_to_async
    def joined_chat(self):
        return self.chat

    @database_sync_to_async
    def disconnect_user(self):
        try:
            profile = UserTechInfo.objects.get(user=self.scope["user"])
            profile.current_channel = ""
            profile.online = False
            profile.save()
        except:
            pass

