import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import CommunityChatMessage

class CommunityChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'community_chat'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        user = data.get('user')
        # Save message to DB
        await self.save_message(user, message)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': user,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'user': event['user'],
        }))

    @sync_to_async
    def save_message(self, user, message):
        CommunityChatMessage.objects.create(user=user, message=message)
