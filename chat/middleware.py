from channels.middleware import BaseMiddleware
from django.conf import settings

class WebSocketCORSMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        headers = [
            (b'Access-Control-Allow-Origin', settings.ALLOWED_HOSTS[0].encode() if settings.ALLOWED_HOSTS else b'*'),
            (b'Access-Control-Allow-Methods', b'GET,POST,OPTIONS'),
            (b'Access-Control-Allow-Headers', b'authorization,content-type'),
            (b'Access-Control-Allow-Credentials', b'true'),
        ]
        scope['cors_headers'] = headers
        return await super().__call__(scope, receive, send)