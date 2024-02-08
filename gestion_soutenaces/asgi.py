"""
ASGI config for gestion_soutenaces project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
import django 
from channels.routing import ProtocolTypeRouter 
from django.core.asgi import get_asgi_application 
from channels.routing import ProtocolTypeRouter, URLRouter 
import soutenance.routing
from channels.auth import AuthMiddlewareStack 
from channels.security.websocket import AllowedHostsOriginValidator
from soutenance.consumers import *
from django.urls import re_path ,path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_soutenaces.settings')


#application = get_asgi_application()
application = ProtocolTypeRouter({ 
  'http': get_asgi_application(), 
  'websocket':AuthMiddlewareStack(URLRouter(soutenance.routing.websocket_urlpatterns)),
})