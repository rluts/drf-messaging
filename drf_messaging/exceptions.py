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


class DRFMError(Exception):
    def __init__(self, msg, status_code):
        self.msg = msg
        self.status_code = status_code


def rest_exception(message, status_code):
    status_dict = {
        400: status.HTTP_400_BAD_REQUEST,
        401: status.HTTP_401_UNAUTHORIZED,
        404: status.HTTP_404_NOT_FOUND,
        500: status.HTTP_500_INTERNAL_SERVER_ERROR
    }
    response = Response(
        {
            'error': {
                'status': status_code,
                'message': message
            }
        }, status=status_dict.get(status_code, None) or status_dict[500]
    )
    return response
