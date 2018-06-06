from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Messages
from .serializers import MessageSerializer, GetChatsSerializer, UploadAttachmentSerializer, ReportSerializer


class SendMessageView(ModelViewSet):
    serializer_class = MessageSerializer


class MessagesView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = MessageSerializer


class GetChatView(MessagesView):
    def get(self, request, *args, **kwargs):
        receiver = request.GET.get('receiver')
        self.queryset = Messages.objects.get_chat(request.user.id, receiver)
        return super().get(request, *args, **kwargs)


class GetChatsView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = GetChatsSerializer

    def get(self, request, *args, **kwargs):
        self.queryset = Messages.objects.get_chats(request.user.id)
        return super().get(request, *args, **kwargs)


class InboxMessagesView(MessagesView):
    def get(self, request, *args, **kwargs):
        self.queryset = Messages.objects.get_inbox(request.user)
        return super().get(request, *args, **kwargs)


class OutboxMessagesView(MessagesView):
    def get(self, request, *args, **kwargs):
        self.queryset = Messages.objects.get_outbox(request.user)
        return super().get(request, *args, **kwargs)


class UploadAttachmentView(ModelViewSet):
    serializer_class = UploadAttachmentSerializer


class ReportMessageView(ModelViewSet):
    serializer_class = ReportSerializer
