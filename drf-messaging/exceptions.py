from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def api_exception_handler(exc, context):
    """
    api errors exceptions.
    Set 'EXCEPTION_HANDLER': 'yoga_messages.exceptions.api_exception_handler'
    in your rest rest framework settings
    :param exc:
    :param context:
    :return:
    """
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