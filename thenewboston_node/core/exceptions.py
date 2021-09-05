from rest_framework import status
from rest_framework.exceptions import APIException


class ClientSideAPIError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Malformed request.'
    default_code = 'client_side_error'


class NotImplementAPIError(APIException):
    status_code = status.HTTP_501_NOT_IMPLEMENTED
    default_detail = 'Not implemented'
    default_code = 'not_implemented'
