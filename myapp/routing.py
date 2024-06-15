from django.urls import re_path
from .consumer import ContactConsumer

websocket_urlpatterns = [
    re_path(r'ws/contacts/$', ContactConsumer.as_asgi()),
]
