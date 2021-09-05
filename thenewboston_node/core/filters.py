from rest_framework.filters import OrderingFilter


class SingleFieldReversibleOrderingFilter(OrderingFilter):

    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)
        if not ordering:
            return queryset

        assert len(ordering) == 1
        return reversed(queryset) if ordering[0].startswith('-') else queryset

    def get_valid_fields(self, queryset, view, context=None):
        valid_fields = super().get_valid_fields(queryset, view, context=context or {})
        assert len(valid_fields) == 1
        return valid_fields
