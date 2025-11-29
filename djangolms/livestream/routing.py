"""
WebSocket URL routing for livestreaming
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/stream/(?P<stream_id>\d+)/$', consumers.LiveStreamConsumer.as_asgi()),
]
