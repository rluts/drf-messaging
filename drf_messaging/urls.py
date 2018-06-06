from django.urls import path
from .views import (
    GetChatView, InboxMessagesView, OutboxMessagesView,
    SendMessageView, GetChatsView, UploadAttachmentView,
    ReportMessageView
)
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet

urlpatterns = [
    path('chat/', GetChatView.as_view()),
    path('chats/', GetChatsView.as_view()),
    path('inbox/', InboxMessagesView.as_view()),
    path('outbox/', OutboxMessagesView.as_view()),
    path('send/', SendMessageView.as_view({'post': 'create'})),
    path('attachments/', UploadAttachmentView.as_view({'post': 'create'})),
    path('report/', ReportMessageView.as_view({'post': 'create'})),
    path('devices/', FCMDeviceAuthorizedViewSet.as_view({'post': 'create'}), name='create_fcm_device')
]