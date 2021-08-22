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


class CustomNoCountLimitOffsetPagination(CustomLimitOffsetPagination):

    def paginate_queryset(self, queryset, request, view=None):
        self.limit = self.get_limit(request)
        if self.limit is None:
            return None

        self.offset = self.get_offset(request)
        self.request = request
        self.display_page_controls = True

        return queryset[self.offset:self.offset + self.limit]

    def get_paginated_dict(self, data):
        return {
            'results': data,
        }
