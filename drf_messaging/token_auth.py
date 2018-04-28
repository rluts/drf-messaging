from rest_framework.authtoken.models import Token


class TokenAuthMiddleware:
    """
    Token authorization middleware for Django Channels 2
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        query = dict((x.split('=') for x in scope['query_string'].decode().split("&")))
        token = query['token']
        token = Token.objects.get(key=token)
        scope['user'] = token.user
        return self.inner(scope)
