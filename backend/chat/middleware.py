from channels.middleware import BaseMiddleware

def JwtAuthMiddlewareStack(inner):
    return inner
