import json
from django.utils.timezone import now
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Conversation, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """ Connect user to a WebSocket chat room using conversation ID """
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]

        # Validate conversation ID
        self.conversation = await self.get_conversation(self.conversation_id)
        if not self.conversation or not await self.is_user_in_conversation(self.user.id, self.conversation_id):
            await self.close()
            return

        # Room name is now the conversation ID
        self.room_group_name = f"chat_{self.conversation_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """ Disconnect user from WebSocket """
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """ Receives a message and sends it to the chat group """
        data = json.loads(text_data)
        message = data.get("message", "").strip()

        if not message:
            return  # Ignore empty messages

        # Save message in the database with timezone-aware timestamp
        saved_message = await self.save_message(self.conversation_id, self.user.id, message, now())

        # Broadcast the message with ISO timestamp
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": saved_message.content,
                "sender_id": saved_message.sender.id,
                "sender_name": saved_message.sender.username,
                "timestamp": saved_message.timestamp.isoformat(),  # Use ISO format
            }
        )

    async def chat_message(self, event):
        """ Sends message to WebSocket """
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_conversation(self, conversation_id):
        """ Get conversation by ID """
        try:
            return Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return None

    @database_sync_to_async
    def is_user_in_conversation(self, user_id, conversation_id):
        """ Check if user is a participant in the conversation """
        return Conversation.objects.filter(id=conversation_id, participants__id=user_id).exists()

    @database_sync_to_async
    def save_message(self, conversation_id, sender_id, content, timestamp):
        """ Save message to the database with timestamp """
        sender = User.objects.get(id=sender_id)
        conversation = Conversation.objects.get(id=conversation_id)
        return Message.objects.create(conversation=conversation, sender=sender, content=content, timestamp=timestamp)


class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """ Connect user to the group chat WebSocket """
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        self.group_id = self.scope["url_route"]["kwargs"]["group_id"]

        # Validate if the group exists
        self.conversation = await self.get_conversation(self.group_id)
        if not self.conversation or not self.conversation.is_groupchat:
            await self.close()
            return

        self.room_group_name = f"groupchat_{self.group_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """ Remove user from group chat """
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """ Handle messages sent to the group """
        data = json.loads(text_data)
        message = data.get("message", "").strip()

        if not message:
            return  # Ignore empty messages

        # Save the message to the database
        saved_message = await self.save_message(self.group_id, self.user.id, message)

        # Broadcast message to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": saved_message.content,
                "sender_id": saved_message.sender.id,
                "sender_name": saved_message.sender.username,
                "timestamp": saved_message.timestamp.isoformat(),
                "chat_id": self.conversation.id  # Include chat_id for frontend sorting
            }
        )

    async def chat_message(self, event):
        """ Send the received message to WebSocket clients """
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_conversation(self, group_id):
        """ Get the group conversation by ID """
        try:
            return Conversation.objects.get(id=group_id, is_groupchat=True)
        except Conversation.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, group_id, sender_id, content):
        """ Save message to database """
        sender = User.objects.get(id=sender_id)
        conversation = Conversation.objects.get(id=group_id)
        return Message.objects.create(conversation=conversation, sender=sender, content=content)
    
    # In your consumer.py or routing logic
    async def extension_popup(self, event):
        await self.send_json({
            'type': 'show_extension_popup',
            'conversation_id': event['conversation_id'],
            'message': event['message'],
    })