from django.urls import path
from .views import (
    GetChatView, InboxMessagesView, OutboxMessagesView,
    SendMessageView, GetChatsView, UploadAttachmentView,
    ReportMessageView
)

urlpatterns = [
    path('chat/', GetChatView.as_view()),
    path('chats/', GetChatsView.as_view()),
    path('inbox/', InboxMessagesView.as_view()),
    path('outbox/', OutboxMessagesView.as_view()),
    path('send/', SendMessageView.as_view({'post': 'create'})),
    path('attachments/', UploadAttachmentView.as_view({'post': 'create'})),
    path('report/', ReportMessageView.as_view({'post': 'create'})),
]
