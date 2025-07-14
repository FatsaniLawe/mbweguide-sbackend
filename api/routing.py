from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/community_chat/$', consumers.CommunityChatConsumer.as_asgi()),
]
