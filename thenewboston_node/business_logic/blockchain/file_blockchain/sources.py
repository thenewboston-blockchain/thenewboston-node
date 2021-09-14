from collections.abc import Iterator

import msgpack
from more_itertools import always_reversible

from thenewboston_node.business_logic.models import Block


class BinaryDataBlockSource(Iterator):

    def __init__(self, binary_data, direction=1):
        assert direction in (1, -1)

        self._binary_data = binary_data
        self.direction = direction
        self._unpacker = None

    @property
    def binary_data(self):
        return self._binary_data

    @property
    def unpacker(self):
        if (unpacker := self._unpacker) is None:
            unpacker = msgpack.Unpacker()
            unpacker.feed(self.binary_data)
            if self.direction == -1:
                unpacker = always_reversible(unpacker)

            self._unpacker = unpacker

        return unpacker

    def __next__(self):
        return Block.from_compact_dict(next(self.unpacker))


class BinaryDataStreamBlockSource(BinaryDataBlockSource):

    def __init__(self, binary_data_stream, direction=1):
        self.binary_data_stream = binary_data_stream

        super().__init__(None, direction=direction)

    @property
    def binary_data(self):
        if (binary_data := self._binary_data) is None:
            # TODO(dmu) LOW: Later we may need to read data in chunk (in case of longer data streams)
            self._binary_data = binary_data = self.binary_data_stream.read()

        return binary_data
