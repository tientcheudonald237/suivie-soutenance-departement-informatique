from . import consumers
from django.urls import re_path ,path

websocket_urlpatterns = [ 
    re_path(r'ws/livec/public_room/', consumers.DocConsumer.as_asgi()), 
] 