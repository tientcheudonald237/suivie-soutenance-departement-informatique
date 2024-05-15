"""
WSGI config for gestion_soutenaces project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import soutenance.routing 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_soutenaces.settings')

application = get_wsgi_application()

app = application


application = ProtocolTypeRouter({
    "https": get_asgi_application(),  
    "websocket": AuthMiddlewareStack(
        URLRouter(
            soutenance.routing.websocket_urlpatterns 
        )
    ),
})
