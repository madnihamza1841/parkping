from django.urls import path
from .views import StartChatView, ThreadListView, MessageListCreateView, BlockView, UnblockView

urlpatterns = [
    path('start/<uuid:car_uuid>/', StartChatView.as_view(), name='chat-start'),
    path('threads/', ThreadListView.as_view(), name='chat-threads'),
    path('<uuid:thread_id>/messages/', MessageListCreateView.as_view(), name='chat-messages'),
    path('<uuid:thread_id>/block/', BlockView.as_view(), name='chat-block'),
    path('<uuid:thread_id>/unblock/', UnblockView.as_view(), name='chat-unblock'),
]
