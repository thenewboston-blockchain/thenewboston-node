from itertools import islice

from more_itertools import always_reversible


class SliceableCountableIterable:

    def __init__(self, source, count=None):
        self.source = source
        self.count = count

    def count(self):
        count = self.count
        if count is None:
            raise TypeError(f"object of type '{type(self).__name__}' has no count()")

        return count() if callable(count) else count

    def __next__(self):
        # Do not call next(self) because it will result in duplicate calls to __getitem__()
        return next(self.source)

    def __getitem__(self, item):
        if isinstance(item, slice):
            return SliceableCountableIterable(islice(self, item.start, item.stop, item.step), count=self.count)

        try:
            return next(self)
        except StopIteration:
            raise IndexError(str(item))


class SliceableReversibleCountableIterable(SliceableCountableIterable):

    def __init__(self, source, reversed_source=None, count=None):
        super().__init__(source, count=count)
        self.reversed_source = reversed_source

    def __reversed__(self):
        source = self.source
        reversed_source = self.reversed_source
        if reversed_source is None:
            # TODO(dmu) LOW: Return SliceableReversibleCountableIterable in case source is reversible
            return SliceableCountableIterable(source=always_reversible(source), count=self.count)

        return SliceableReversibleCountableIterable(source=reversed_source, reversed_source=source, count=self.count)


class FilterableIterator(SliceableReversibleCountableIterable):

    def __init__(self, *args, **kwargs):
        count = kwargs.pop('count', None)
        if count is not None:
            raise NotImplementedError('count argument is not compatible with filtered iterator')

        self.filters = kwargs.pop('filters', None) or []
        super().__init__(*args, **kwargs)

    def add_filter(self, filter_function):
        self.filters.append(filter_function)
        return self

    def __next__(self):
        while True:
            item = super().__next__()
            for filter_function in self.filters:
                if not filter_function(item):
                    break
            else:
                return item

    def __getitem__(self, item):
        if isinstance(item, slice):
            return FilterableIterator(
                islice(self, item.start, item.stop, item.step), count=self.count, filters=self.filters
            )

        return super().__getitem__(item)
