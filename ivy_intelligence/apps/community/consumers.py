"""
Django Channels WebSocket consumer for real-time group chat.

How it works:
1. User connects to ws://site/ws/chat/<group_id>/
2. Consumer joins a channel group named "chat_<group_id>"
3. When a message is received, it's broadcast to all users in that group
4. Message is also saved to the DB (ChatMessage model)

To run with WebSockets, you MUST use Daphne (ASGI server) instead of Gunicorn.
Command: daphne -p 8000 config.asgi:application
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        """Called when a WebSocket connection is established."""
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.room_group_name = f'chat_{self.group_id}'

        # Join the channel group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Send last 20 messages on connect
        messages = await self.get_recent_messages()
        for msg in messages:
            await self.send(text_data=json.dumps({
                'type': 'history',
                'username': msg['sender__username'],
                'message': msg['message'],
                'time': msg['sent_at'].strftime('%H:%M') if msg['sent_at'] else '',
            }))

    async def disconnect(self, close_code):
        """Called when WebSocket connection closes."""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Called when a message is received from the WebSocket client."""
        try:
            data = json.loads(text_data)
            message = data.get('message', '').strip()
            if not message:
                return

            user = self.scope['user']
            if not user.is_authenticated:
                return

            # Save to database
            await self.save_message(user, message)

            # Broadcast to all users in the group channel
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',  # maps to the method below
                    'message': message,
                    'username': user.username,
                    'time': timezone.now().strftime('%H:%M'),
                }
            )
        except json.JSONDecodeError:
            pass

    async def chat_message(self, event):
        """
        Called when a message is broadcast to the channel group.
        Sends it to the individual WebSocket client.
        """
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'username': event['username'],
            'time': event['time'],
        }))

    @database_sync_to_async
    def save_message(self, user, message):
        """Save a chat message to the database (runs synchronously in async context)."""
        from apps.community.models import ChatMessage, DomainGroup
        try:
            group = DomainGroup.objects.get(pk=self.group_id)
            ChatMessage.objects.create(group=group, sender=user, message=message)
        except DomainGroup.DoesNotExist:
            pass

    @database_sync_to_async
    def get_recent_messages(self):
        """Retrieve last 20 messages for chat history."""
        from apps.community.models import ChatMessage
        messages = ChatMessage.objects.filter(
            group_id=self.group_id
        ).select_related('sender').values(
            'sender__username', 'message', 'sent_at'
        ).order_by('-sent_at')[:20]
        return list(reversed(messages))
