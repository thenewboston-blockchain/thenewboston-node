from rest_framework import status
from rest_framework.exceptions import APIException


class ClientSideAPIError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Malformed request.'
    default_code = 'client_side_error'
