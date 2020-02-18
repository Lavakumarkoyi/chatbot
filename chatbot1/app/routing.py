from django.urls import path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    path('chat/<username>/<bot_id>', ChatConsumer),
]
