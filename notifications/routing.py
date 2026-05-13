"""
WebSocket routing configuration for notifications

Defines the WebSocket URL patterns for the notification system.
Only active if ENABLE_WEBSOCKET_NOTIFICATIONS is True.
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]
