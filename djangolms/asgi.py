"""
ASGI config for djangolms project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangolms.settings')

# Initialize Django ASGI application early to populate apps registry
django_asgi_app = get_asgi_application()

# Import channels components after Django setup
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from djangolms.chat.routing import websocket_urlpatterns as chat_websockets
from djangolms.livestream.routing import websocket_urlpatterns as stream_websockets

# Combine WebSocket URL patterns
websocket_urlpatterns = chat_websockets + stream_websockets

application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    "http": django_asgi_app,

    # WebSocket chat handler with authentication
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
