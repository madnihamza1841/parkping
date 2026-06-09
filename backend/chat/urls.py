from django.urls import path
from .views import StartChatView, ThreadListView, MessageListCreateView

urlpatterns = [
    path('start/<uuid:car_uuid>/', StartChatView.as_view(), name='chat-start'),
    path('threads/', ThreadListView.as_view(), name='chat-threads'),
    path('<uuid:thread_id>/messages/', MessageListCreateView.as_view(), name='chat-messages'),
]
