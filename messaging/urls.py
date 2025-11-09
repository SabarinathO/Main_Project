from django.urls import path
from .views import get_or_create_conversation, send_message, chatInterface, group_chat, new_groupChat,profile,home,handle_extension_decision

urlpatterns = [
    path("chat/<int:user_id>/", get_or_create_conversation, name="chat"),  # Finding or creating a conversation
    path("chat/conversation/<int:conversation_id>/", send_message, name="send_message"),  # Sending messages
    path("chat/", chatInterface, name="chatInterface"), # Chat interface
    path("groupchat/", new_groupChat, name="groupChat"),  # Group chat
    path("groupchat/<int:group_id>/", group_chat, name="groupchat"),  # Group chat interface
    path("profile/", profile, name="profile"),  # User profile
    path("main/", home, name="main"),  # Home page
    path("group/extend/<int:conversation_id>/", handle_extension_decision, name="handle_extension_decision"),

]
