from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import *
from django.template.loader import render_to_string
from asgiref.sync import sync_to_async

class ChatroomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name']
        self.chatroom = await self.get_chatroom()
        if not self.chatroom:
            await self.close()
            return

        await self.channel_layer.group_add(self.chatroom_name, self.channel_name)
        await self.accept()

        if self.user.is_authenticated:
            await self.add_user_online_if_missing()
            await self.update_online_count()

    async def disconnect(self, close_code):
        if hasattr(self, "chatroom_name"):
            await self.channel_layer.group_discard(self.chatroom_name, self.channel_name)

        if (
            hasattr(self, "chatroom")
            and self.chatroom
            and hasattr(self, "user")
            and self.user.is_authenticated
            and await self.user_is_online()
        ):
            await self.remove_user_online()
            await self.update_online_count()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        body = text_data_json['body']
        message = await self.create_message(body)
        event = {
            'type': 'message_handler',
            'message_id': message.id,
        }
        await self.channel_layer.group_send(self.chatroom_name, event)

    async def message_handler(self, event):
        message_id = event['message_id']
        message = await self.get_message(message_id)
        if not message:
            return

        context = {
            'msg': message,
            'user': self.user,
            'chat_group': self.chatroom
        }
        html = await sync_to_async(render_to_string)("rt_chat/partials/chat_message_p.html", context=context)
        await self.send(text_data=html)

    async def update_online_count(self):
        online_count = await self.get_online_count_minus_self()
        event = {
            'type': 'online_count_handler',
            'online_count': online_count
        }
        await self.channel_layer.group_send(self.chatroom_name, event)

    async def online_count_handler(self, event):
        online_count = event['online_count']
        users = await self.get_recent_chat_authors()
        context = {
            'online_count': online_count,
            'chat_group': self.chatroom,
            'users': users
        }
        html = await sync_to_async(render_to_string)("rt_chat/partials/online_count.html", context)
        await self.send(text_data=html)

    @sync_to_async
    def get_chatroom(self):
        try:
            return ChatGroup.objects.get(group_name=self.chatroom_name)
        except ChatGroup.DoesNotExist:
            return None

    @sync_to_async
    def add_user_online_if_missing(self):
        if self.user not in self.chatroom.users_online.all():
            self.chatroom.users_online.add(self.user)

    @sync_to_async
    def user_is_online(self):
        return self.user in self.chatroom.users_online.all()

    @sync_to_async
    def remove_user_online(self):
        self.chatroom.users_online.remove(self.user)

    @sync_to_async
    def create_message(self, body):
        return GroupMessage.objects.create(
            body=body,
            author=self.user,
            group=self.chatroom
        )

    @sync_to_async
    def get_message(self, message_id):
        try:
            return GroupMessage.objects.get(id=message_id)
        except GroupMessage.DoesNotExist:
            return None

    @sync_to_async
    def get_online_count_minus_self(self):
        return self.chatroom.users_online.count() - 1

    @sync_to_async
    def get_recent_chat_authors(self):
        chat_messages = ChatGroup.objects.get(group_name=self.chatroom_name).chat_messages.all()[:30]
        author_ids = set([message.author.id for message in chat_messages])
        return list(User.objects.filter(id__in=author_ids))


class OnlineStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.group_name = 'online-status'
        self.group = await self.get_group()
        if not self.group:
            await self.close()
            return

        await self.accept()

        if self.user.is_authenticated:
            await self.add_user_online_if_missing()
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.online_status()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

        if (
            hasattr(self, "group")
            and self.group
            and hasattr(self, "user")
            and self.user.is_authenticated
            and await self.user_is_online()
        ):
            await self.remove_user_online()

        if hasattr(self, "group") and self.group:
            await self.online_status()

    async def online_status(self):
        event = {
            "type": 'online_status_handler'
        }
        await self.channel_layer.group_send(self.group_name, event)

    async def online_status_handler(self, event):
        if not self.user.is_authenticated:
            return

        online_users, public_chat_users, online_in_chats = await self.get_online_status_context_data()
        context = {
            'online_users': online_users,
            'online_in_chats': online_in_chats,
            'public_chat_users': public_chat_users,
            'user': self.user
        }
        html = await sync_to_async(render_to_string)('rt_chat/partials/online_status.html', context)
        await self.send(text_data=html)

    @sync_to_async
    def get_group(self):
        try:
            return ChatGroup.objects.get(group_name=self.group_name)
        except ChatGroup.DoesNotExist:
            return None

    @sync_to_async
    def add_user_online_if_missing(self):
        if self.user not in self.group.users_online.all():
            self.group.users_online.add(self.user)

    @sync_to_async
    def user_is_online(self):
        return self.user in self.group.users_online.all()

    @sync_to_async
    def remove_user_online(self):
        self.group.users_online.remove(self.user)

    @sync_to_async
    def get_online_status_context_data(self):
        online_users = list(self.group.users_online.exclude(id=self.user.id))
        try:
            public_chat_users = list(ChatGroup.objects.get(group_name='school-gc').users_online.exclude(id=self.user.id))
        except ChatGroup.DoesNotExist:
            public_chat_users = []

        my_chats = self.user.chat_groups.all()
        private_chats_with_users = [
            chat for chat in my_chats.filter(is_private=True)
            if chat.users_online.exclude(id=self.user.id).exists()
        ]
        group_chats_with_users = [
            chat for chat in my_chats.filter(groupchat_name__isnull=False)
            if chat.users_online.exclude(id=self.user.id).exists()
        ]

        online_in_chats = bool(public_chat_users or private_chats_with_users or group_chats_with_users)
        return online_users, public_chat_users, online_in_chats
