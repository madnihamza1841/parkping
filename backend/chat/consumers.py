import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatThread, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.thread_id = self.scope['url_route']['kwargs']['thread_id']
        self.room_group_name = f'chat_{self.thread_id}'
        user = self.scope.get('user')

        if not user or not user.is_authenticated:
            await self.close()
            return

        thread = await self.get_thread(self.thread_id)
        if not thread:
            await self.close()
            return

        if not await self.user_in_thread(user, thread):
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data.get('content', '').strip()
        if not content:
            return

        user = self.scope['user']
        msg = await self.save_message(user, content)
        sender_label = await self.get_sender_label(msg)

        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'chat_message',
            'uuid': str(msg.uuid),
            'sender_label': sender_label,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat(),
        })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'uuid': event['uuid'],
            'sender_label': event['sender_label'],
            'content': event['content'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def get_thread(self, thread_id):
        try:
            return ChatThread.objects.select_related('car__owner').get(uuid=thread_id)
        except ChatThread.DoesNotExist:
            return None

    @database_sync_to_async
    def user_in_thread(self, user, thread):
        return user == thread.scanner or user == thread.car.owner

    @database_sync_to_async
    def save_message(self, user, content):
        thread = ChatThread.objects.get(uuid=self.thread_id)
        return Message.objects.create(thread=thread, sender=user, content=content)

    @database_sync_to_async
    def get_sender_label(self, msg):
        return msg.thread.get_sender_label(msg.sender)
