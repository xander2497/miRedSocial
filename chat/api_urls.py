from django.urls import path
from .api_views import *


app_name = "chat_api"

urlpatterns = [
    path("conversations/",MyConversationsAPIView.as_view(), name='my_conversations'),
    path("start/<int:user_id>/",StartConversationAPIView.as_view(),name="start_conversation"),
    path("<int:convo_id>/messages/", ConversationsMessagesAPIView.as_view(),name='conversations_messages'),
    path("<int:convo_id>/send/", SendMessageAPIView.as_view(),name="send_message")
]