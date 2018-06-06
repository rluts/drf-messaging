from rest_framework import serializers
from .models import Messages, User, ReportedMessages, Attachment
from .validators import blacklist_validator, ValidationError
from .utils import get_user_info_from_instance


class UploadAttachmentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Attachment
        fields = ('id', 'file')

    def validate(self, attrs):
        attrs['owner'] = self.context['request'].user
        return super().validate(attrs)


class MessageSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    message = serializers.CharField(validators=(blacklist_validator,), required=False)
    datetime = serializers.DateTimeField(read_only=True)
    read = serializers.BooleanField(read_only=True)
    attachments = serializers.PrimaryKeyRelatedField(many=True, queryset=Attachment.objects.all())

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['sender'] = get_user_info_from_instance(instance.sender)
        data['receiver'] = get_user_info_from_instance(instance.receiver)
        data['attachments'] = [{
            'file': self.context['request'].build_absolute_uri(i.file.url)
        } for i in instance.attachments.all()]
        return data

    def create(self, validated_data):
        mes = Messages.objects.send_message(**validated_data, sender=self.context['request'].user)
        mes.attachments.set(validated_data['attachments'])
        mes.save()
        return mes


class GetChatsSerializer(serializers.Serializer):
    user = serializers.IntegerField()
    unread_messages = serializers.IntegerField()
    last_message = serializers.SerializerMethodField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = get_user_info_from_instance(User.objects.get(id=data['user']))
        return data

    def get_last_message(self, instance):
        message = Messages.objects.get(id=instance['last_message_id'])
        response = {
                'message': message.message,
                'datetime': message.datetime,
                'sender': get_user_info_from_instance(message.sender),
                'receiver': get_user_info_from_instance(message.receiver)
        }
        return response


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportedMessages
        fields = ('datetime', 'message', 'comment')

    def validate(self, attrs):
        if attrs['message'].receiver != self.context['request'].user:
            raise ValidationError("You are not receiver of this message")
        attrs['reporter'] = self.context['request'].user
        return super().validate(attrs)
