import logging
from collections.abc import Iterator, Reversible
from itertools import islice

from more_itertools import always_reversible

logger = logging.getLogger(__name__)


class FilteringNextMixin:

    def __next__(self):
        while True:
            # Do not call next(self) because it will result in duplicate calls to __getitem__()
            item = next(self.source)
            for filter_function in self.filters:
                if not filter_function(item):
                    break
            else:
                return item


class LazyReversed(Iterator):

    def __init__(self, source):
        self.source = source
        self._reversed_source = None

    @property
    def reversed_source(self):
        if (reversed_source := self._reversed_source) is None:
            self._reversed_source = reversed_source = always_reversible(self.source)

        return reversed_source

    def __next__(self):
        return next(self.reversed_source)


class LazyFiltered(FilteringNextMixin, Iterator):

    def __init__(self, source, filters):
        self.source = source
        self.filters = filters


class AdvancedIterator(FilteringNextMixin, Iterator, Reversible):

    def __init__(self, source, *, reversed_source=None, filters=None, count=None):
        self.source = source
        self._reversed_source = reversed_source
        if filters and count is not None:
            raise NotImplementedError('`filters` and `count` are not compatible')

        self._count = count
        self.filters = filters or []

    def count(self):
        # TODO(dmu) LOW: Implement low performance count (if count argument is not provided) that works
        #                like ilen(self.source). It should not respect slicing (still count sliced out values),
        #                but respect filtering
        count = self._count
        if count is None:
            raise TypeError(f"object of type '{type(self).__name__}' has no count()")

        return count() if callable(count) else count

    @property
    def reversed_source(self):
        if (reversed_source := self._reversed_source) is None:
            logger.warning('Possibly low performance reversed_source is in use')
            source = self.source
            try:
                reversed_source = reversed(source)
            except TypeError:
                reversed_source = LazyReversed(source)

            self._reversed_source = reversed_source

        return reversed_source

    def __getitem__(self, item):
        if isinstance(item, slice):
            # TODO(dmu) MEDIUM: Support callable `source` argument to propagate `slice` object intto, so to allow
            #                   implementation specific optimizations for slicing
            source = self.source
            filters = self.filters
            if filters:
                source = LazyFiltered(source, filters)

            sliced = islice(source, item.start, item.stop, item.step)
            # TODO(dmu) HIGH: `reversed_source=LazyReversed(sliced)` ignores provided `reversed_source` argument
            #                 which results in using low performance `source`. Fix it by properly recalculating
            #                 `item.start, item.stop, item.step` values so we can slice `reversed_source`
            #                 instead of slicing reversed `source`
            logger.warning('Possibly low performance reversing is in use')
            return self.clone(source=sliced, reversed_source=LazyReversed(sliced))

        try:
            return next(self)
        except StopIteration:
            raise IndexError(str(item))

    def __reversed__(self):
        return self.clone(source=self.reversed_source, reversed_source=self.source)

    def add_filter(self, filter_function):
        if self._count is not None:
            raise NotImplementedError('Cannot add filter to an iterator with count')

        self.filters.append(filter_function)

    def clone(self, **kwargs):
        kwargs.setdefault('source', self.source)
        kwargs.setdefault('reversed_source', self.reversed_source)
        kwargs.setdefault('filters', self.filters.copy())
        kwargs.setdefault('count', self._count)
        return self.__class__(**kwargs)
