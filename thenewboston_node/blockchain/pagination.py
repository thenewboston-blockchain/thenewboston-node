from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class CustomLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 5
    max_limit = 20

    def get_paginated_dict(self, data):
        return {
            'count': self.count,
            'results': data,
        }

    def get_paginated_response(self, data):
        return Response(self.get_paginated_dict(data))
