from itertools import islice


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
            return next(self.source)
        except StopIteration:
            raise IndexError(str(item))
