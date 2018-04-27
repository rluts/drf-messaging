from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


class ClientError(Exception):
    """
    Custom exception class that is caught by the websocket receive()
    handler and translated into a send back to the client.
    """
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def api_exception_handler(exc, context):
    try:
        message = str(exc.args[0])
        code = int(exc.args[1])
        status_dict = {
            400: status.HTTP_400_BAD_REQUEST,
            401: status.HTTP_401_UNAUTHORIZED,
            404: status.HTTP_404_NOT_FOUND,
            500: status.HTTP_500_INTERNAL_SERVER_ERROR
        }
        response = Response({"error": {"code": code, "message": message}}, status=status_dict[code])
    except:
        response = exception_handler(exc, context)

    return response
