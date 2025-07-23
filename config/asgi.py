import os
import django

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import notification.routing


from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
from config.middleware import AllowedOriginMiddleware
from notification.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            notification.routing.websocket_urlpatterns
        )
    ),
    
    # "websocket": AllowedHostsOriginValidator(
    #     URLRouter(notification.routing.websocket_urlpatterns)
    # ),
    
    #  "websocket": AllowedOriginMiddleware(
    #     AuthMiddlewareStack(
    #         URLRouter(websocket_urlpatterns)
    #     )
    # ),
})
