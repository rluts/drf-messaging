from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from .consumers import SocketCostumer
from .token_auth import TokenAuthMiddleware

application = ProtocolTypeRouter({

    # Channels will do this for you automatically. It's included here as an example.
    # "http": AsgiHandler,

    # Route all WebSocket requests to our custom chat handler.
    # We actually don't need the URLRouter here, but we've put it in for
    # illustration. Also note the inclusion of the AuthMiddlewareStack to
    # add users and sessions - see http://channels.readthedocs.io/en/latest/topics/authentication.html
    "websocket": TokenAuthMiddleware(
        URLRouter([
            path("socket/", SocketCostumer),
        ]),
    ),

})