from django.urls import re_path
from messaging.consumers import ChatConsumer, GroupChatConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<conversation_id>\d+)/$", ChatConsumer.as_asgi()),  # Private Chat
    re_path(r"ws/groupchat/(?P<group_id>\d+)/$", GroupChatConsumer.as_asgi()),  # Group Chat
]
