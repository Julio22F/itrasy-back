from urllib.parse import urlparse

class AllowedOriginMiddleware:
    def __init__(self, app):
        self.app = app
        self.allowed_origins = [
            "http://localhost:3000",
            "https://nancy-levels-hour-stating.trycloudflare.com",
            "https://propecia-rolls-connectivity-zshops.trycloudflare.com",
            "*"  # optionnel, à retirer en prod
        ]

    async def __call__(self, scope, receive, send):
        headers = dict(scope.get("headers", []))
        origin = headers.get(b'origin', b'').decode()

        if "*" in self.allowed_origins or origin in self.allowed_origins:
            return await self.app(scope, receive, send)
        else:
            # Refuser la connexion WebSocket
            if scope["type"] == "websocket":
                await send({
                    "type": "websocket.close",
                    "code": 4030
                })
            return
