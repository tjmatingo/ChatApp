"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# to enable websocket connection
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

django_asgi_application = get_asgi_application()

from rt_chat import routing


application = ProtocolTypeRouter({
    'http': django_asgi_application,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns))
    ),
})

