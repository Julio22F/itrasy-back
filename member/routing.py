from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/notifications/<int:member_id>/", consumers.NotificationConsumer.as_asgi()),
]
