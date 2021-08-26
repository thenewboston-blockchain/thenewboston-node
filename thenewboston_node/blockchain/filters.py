from rest_framework.filters import OrderingFilter


class BlockchainStateMetaOrderingFilter(OrderingFilter):
    ordering_fields = ('last_block_number',)

    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)
        if ordering:
            assert len(ordering) == 1
            if '-last_block_number' in ordering:
                queryset = reversed(queryset)

        return queryset
