from rest_framework import serializers
from .models import Messages, User


class MessageSerializer(serializers.Serializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    message = serializers.CharField()
    datetime = serializers.DateTimeField(read_only=True)
    read = serializers.BooleanField(read_only=True)

    def create(self, validated_data):
        return Messages.objects.send_message(**validated_data, sender=self.context['request'].user)


class GetChatsSerializer(serializers.Serializer):
    user = serializers.IntegerField()
    unread_messages = serializers.IntegerField()
    last_message = serializers.SerializerMethodField()

    def get_last_message(self, instance):
        message = Messages.objects.get(id=instance['last_message_id'])
        response = {
                'message': message.message,
                'datetime': message.datetime,
                'sender': message.sender.id,
                'receiver': message.receiver.id
        }
        return response
