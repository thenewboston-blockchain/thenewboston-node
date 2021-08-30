from rest_framework.filters import OrderingFilter


class TransactionOrderingFilter(OrderingFilter):
    ordering_fields = ('block_number',)

    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)
        if ordering:
            assert len(ordering) == 1
            if '-block_number' in ordering:
                queryset = reversed(queryset)

        return queryset
