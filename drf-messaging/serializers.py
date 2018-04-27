from rest_framework import serializers
from .models import Messages, User, BlackList, Attachment
from .validators import blacklist_validator
from .utils import ExtRelatedField


class UploadAttachmentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Attachment
        fields = ('id', 'file')

    def validate(self, attrs):
        attrs['owner'] = self.context['request'].user
        return super().validate(attrs)


class MessageSerializer(serializers.Serializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    message = serializers.CharField(validators=(blacklist_validator,))
    datetime = serializers.DateTimeField(read_only=True)
    read = serializers.BooleanField(read_only=True)
    attachments = serializers.PrimaryKeyRelatedField(many=True, queryset=Attachment.objects.all())

    def create(self, validated_data):
        mes = Messages.objects.send_message(**validated_data, sender=self.context['request'].user)
        mes.attachments.set(validated_data['attachments'])
        mes.save()
        return mes


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
