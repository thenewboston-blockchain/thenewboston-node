import copy
from functools import partial

from django_filters import FilterSet, NumberFilter
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


class AdvanceIteratorFilterSet(FilterSet):

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        self.is_bound = data is not None
        self.data = data or {}
        self.queryset = queryset
        self.request = request
        self.form_prefix = prefix

        self.filters = copy.deepcopy(self.base_filters)

    def filter_queryset(self, queryset):
        for name, value in self.form.cleaned_data.items():
            queryset = self.filters[name].filter(queryset, value)

        return queryset

    @property
    def qs(self):
        if not hasattr(self, '_qs'):
            self._qs = self.filter_queryset(self.queryset)
        return self._qs


class AdvanceIteratorNumberFilter(NumberFilter):

    def __init__(self, filter_function, *args, **kwargs):
        self.filter_function = filter_function
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):  # noqa: A003
        if value is None:
            return qs

        # TODO(dmu) MEDIUM: Improve filtering performance to avoid traversal of unneeded items
        qs.add_filter(partial(self.filter_function, filter_value=value))
        return qs
