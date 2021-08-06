from collections import OrderedDict

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class CustomLimitOffsetPaginationBase(LimitOffsetPagination):
    default_limit = 5
    max_limit = 20

    def get_paginated_dict(self, data):
        raise NotImplementedError('Must be implemented in a child class')

    def get_paginated_response(self, data):
        return Response(self.get_paginated_dict(data))


class CustomLimitOffsetPagination(CustomLimitOffsetPaginationBase):

    def get_paginated_dict(self, data):
        return OrderedDict((('count', self.count), ('next', self.get_next_link()),
                            ('previous', self.get_previous_link()), ('results', data)))
