from rest_framework.authtoken.models import Token
from django.db import close_old_connections
from django.contrib.auth.models import AnonymousUser


class TokenAuthMiddleware:
    """
    Token authorization middleware for Django Channels 2
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        query = dict((x.split('=') for x in scope['query_string'].decode().split("&")))
        if not query.get('token', None):
            scope['user'] = AnonymousUser()
        else:
            try:
                token = query['token']
                token = Token.objects.get(key=token)
                scope['user'] = token.user
                close_old_connections()
            except Token.DoesNotExist:
                scope['user'] = AnonymousUser()
        return self.inner(scope)
