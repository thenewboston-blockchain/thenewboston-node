from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import APIException


class APINotImplemented(APIException):
    status_code = status.HTTP_501_NOT_IMPLEMENTED
    default_detail = _('Not implemented.')
    default_code = 'not_implemented'
