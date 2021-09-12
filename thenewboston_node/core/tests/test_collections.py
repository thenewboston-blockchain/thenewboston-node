from thenewboston_node.core.utils.collections import replace_keys
from thenewboston_node.core.utils.itertools import (
    FilterableIterator, SliceableCountableIterable, SliceableReversibleCountableIterable
)


def test_replace_keys():
    replace_map = {
        'long_a': 'a',
        'long_b': 'b',
        'long_c': 'c',
        'long_d': 'd',
        'long_e': 'e',
        'long_f': 'f',
    }
    assert replace_keys({'long_a': 1}, replace_map) == {'a': 1}
    assert replace_keys([{'long_a': 1}], replace_map) == [{'a': 1}]
    assert replace_keys({'long_a': 1, 'long_b': 2}, replace_map) == {'a': 1, 'b': 2}
    assert replace_keys({
        'long_a': 1,
        'long_b': 2,
        'long_c': [1, 2, 3]
    }, replace_map) == {
        'a': 1,
        'b': 2,
        'c': [1, 2, 3]
    }
    assert replace_keys({
        'long_a': {
            'long_c': 1
        },
        'long_b': 2,
        'long_c': [1, 2, 3]
    }, replace_map) == {
        'a': {
            'c': 1
        },
        'b': 2,
        'c': [1, 2, 3]
    }
    assert replace_keys({
        'long_a': {
            'long_c': 1
        },
        'long_b': 2,
        'long_c': [{
            'long_d': 4
        }, 2, 3]
    }, replace_map) == {
        'a': {
            'c': 1
        },
        'b': 2,
        'c': [{
            'd': 4
        }, 2, 3]
    }
    assert replace_keys({
        'long_a': {
            'long_c': [1, 5, 6]
        },
        'long_b': 2,
        'long_c': [{
            'long_d': [1, 2, 3]
        }, 2, 3]
    }, replace_map) == {
        'a': {
            'c': [1, 5, 6]
        },
        'b': 2,
        'c': [{
            'd': [1, 2, 3]
        }, 2, 3]
    }


def test_sliceable_countable_iterable():
    generator = (_ for _ in range(10))
    assert list(generator) == list(range(10))

    generator = (_ for _ in range(10))
    assert list(SliceableCountableIterable(generator)) == list(range(10))

    generator = (_ for _ in range(10))
    assert list(SliceableCountableIterable(generator)[2:5]) == [2, 3, 4]

    generator = (_ for _ in range(10))
    sliceable_countable_iterable = SliceableCountableIterable(generator, count=lambda: 10)[2:5]
    assert sliceable_countable_iterable.count() == 10
    assert list(sliceable_countable_iterable) == [2, 3, 4]

    generator = (_ for _ in range(10))
    sliceable_countable_iterable = SliceableCountableIterable(generator, count=lambda: 10)[2:5]
    assert list(sliceable_countable_iterable) == [2, 3, 4]
    assert sliceable_countable_iterable.count() == 10


def test_sliceable_reversible_countable_iterable():
    generator = (_ for _ in range(10))
    assert list(generator) == list(range(10))

    assert list(SliceableReversibleCountableIterable((_ for _ in range(10)))) == list(range(10))
    assert list(reversed(SliceableReversibleCountableIterable((_ for _ in range(10))))) == list(range(9, -1, -1))

    assert list(SliceableReversibleCountableIterable((_ for _ in range(10)))[2:5]) == [2, 3, 4]
    # TODO(dmu) HIGH: Following line fails with " TypeError: object of type 'SliceableCountableIterable' has no len()"
    # assert list(reversed(SliceableReversibleCountableIterable((_ for _ in range(10)))[2:5])) == [4, 3, 2]

    iterable_ = SliceableReversibleCountableIterable((_ for _ in range(10)), count=lambda: 10)[2:5]
    assert iterable_.count() == 10
    assert list(iterable_) == [2, 3, 4]
    # TODO(dmu) HIGH: Following line fails with " TypeError: object of type 'SliceableCountableIterable' has no len()"
    # assert list(reversed(SliceableReversibleCountableIterable((_ for _ in range(10)), count=lambda: 10)[2:5])) == [4, 3, 2]

    iterable_ = SliceableCountableIterable((_ for _ in range(10)), count=lambda: 10)[2:5]
    assert list(iterable_) == [2, 3, 4]
    # TODO(dmu) HIGH: Following line fails with " TypeError: object of type 'SliceableCountableIterable' has no len()"
    # assert list(reversed(SliceableCountableIterable((_ for _ in range(10)), count=lambda: 10)[2:5])) == [4, 3, 2]
    assert iterable_.count() == 10

    # TODO(dmu) HIGH: Add more checks about order of reversed and slicing


def test_filterable_iterator():
    generator = (_ for _ in range(10))
    assert list(FilterableIterator(generator)) == list(range(10))

    generator = (_ for _ in range(10))
    iter_ = FilterableIterator(generator)
    iter_.add_filter(lambda x: x >= 1)
    assert list(iter_) == list(range(1, 10))
