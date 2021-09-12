from thenewboston_node.core.utils.itertools import AdvancedIterator, LazyReversed

ZERO_TO_NINE_TUPLE = tuple(range(10))


def zero_to_nine_generator():
    return (_ for _ in range(10))


def test_lazy_reversed():
    range_generator = zero_to_nine_generator()
    lazy_reversed = LazyReversed(range_generator)
    assert tuple(range_generator) == ZERO_TO_NINE_TUPLE
    assert tuple(lazy_reversed) == ()

    range_generator = zero_to_nine_generator()
    lazy_reversed = LazyReversed(range_generator)
    assert tuple(lazy_reversed) == ZERO_TO_NINE_TUPLE[::-1]
    assert tuple(range_generator) == ()

    range_generator = zero_to_nine_generator()
    lazy_reversed = LazyReversed(range_generator)
    assert next(lazy_reversed) == 9
    assert next(lazy_reversed) == 8
    assert next(lazy_reversed) == 7
    assert tuple(range_generator) == ()
    assert tuple(lazy_reversed) == (6, 5, 4, 3, 2, 1, 0)


def test_advanced_iterator_basic_slicing():
    assert tuple(AdvancedIterator(zero_to_nine_generator())) == ZERO_TO_NINE_TUPLE
    assert tuple(AdvancedIterator(zero_to_nine_generator())[2:5]) == ZERO_TO_NINE_TUPLE[2:5]


def test_advanced_iterator_count():
    adv_iterable = AdvancedIterator(zero_to_nine_generator(), count=10)
    assert adv_iterable.count() == 10
    assert tuple(adv_iterable) == ZERO_TO_NINE_TUPLE
    assert adv_iterable.count() == 10

    adv_iterable = AdvancedIterator(zero_to_nine_generator(), count=10)[2:5]
    assert adv_iterable.count() == 10
    assert tuple(adv_iterable) == ZERO_TO_NINE_TUPLE[2:5]
    assert adv_iterable.count() == 10

    adv_iterable = AdvancedIterator(zero_to_nine_generator(), count=lambda: 10)
    assert adv_iterable.count() == 10
    assert tuple(adv_iterable) == ZERO_TO_NINE_TUPLE
    assert adv_iterable.count() == 10

    adv_iterable = AdvancedIterator(zero_to_nine_generator(), count=lambda: 10)[2:5]
    assert adv_iterable.count() == 10
    assert tuple(adv_iterable) == ZERO_TO_NINE_TUPLE[2:5]
    assert adv_iterable.count() == 10


def test_advanced_iterator_reversed_fallback():
    assert tuple(reversed(AdvancedIterator(zero_to_nine_generator()))) == ZERO_TO_NINE_TUPLE[::-1]


def test_advanced_iterator_reversed():
    assert tuple(reversed(AdvancedIterator(zero_to_nine_generator(),
                                           reversed_source=reversed(ZERO_TO_NINE_TUPLE)))) == ZERO_TO_NINE_TUPLE[::-1]


def test_advanced_iterator_slice_then_reverse():
    source = zero_to_nine_generator()
    reversed_source = reversed(ZERO_TO_NINE_TUPLE)
    assert tuple(reversed(AdvancedIterator(source, reversed_source=reversed_source)[2:5])) == (4, 3, 2)

    source = zero_to_nine_generator()
    assert tuple(reversed(AdvancedIterator(source)[2:5])) == (4, 3, 2)


def test_advanced_iterator_reverse_then_slice():
    source = zero_to_nine_generator()
    reversed_source = reversed(ZERO_TO_NINE_TUPLE)
    assert tuple(reversed(AdvancedIterator(source, reversed_source=reversed_source))[2:5]) == (7, 6, 5)

    source = zero_to_nine_generator()
    assert tuple(reversed(AdvancedIterator(source))[2:5]) == (7, 6, 5)


def test_advanced_iterator_multiple_reverse():
    adv_iterable = AdvancedIterator(zero_to_nine_generator(), reversed_source=reversed(ZERO_TO_NINE_TUPLE))
    assert tuple(adv_iterable) == ZERO_TO_NINE_TUPLE

    adv_iterable = AdvancedIterator(zero_to_nine_generator(), reversed_source=reversed(ZERO_TO_NINE_TUPLE))
    assert tuple(reversed(adv_iterable)) == ZERO_TO_NINE_TUPLE[::-1]

    adv_iterable = AdvancedIterator(zero_to_nine_generator(), reversed_source=reversed(ZERO_TO_NINE_TUPLE))
    assert tuple(reversed(reversed(adv_iterable))) == ZERO_TO_NINE_TUPLE

    adv_iterable = AdvancedIterator(zero_to_nine_generator(), reversed_source=reversed(ZERO_TO_NINE_TUPLE))
    assert tuple(reversed(reversed(reversed(adv_iterable)))) == ZERO_TO_NINE_TUPLE[::-1]

    adv_iterable = AdvancedIterator(zero_to_nine_generator(), reversed_source=reversed(ZERO_TO_NINE_TUPLE))
    assert tuple(reversed(reversed(reversed(reversed(adv_iterable))))) == ZERO_TO_NINE_TUPLE


def test_advanced_iterator_multiple_reverse_fallback():
    adv_iterable = AdvancedIterator(zero_to_nine_generator())
    assert tuple(adv_iterable) == ZERO_TO_NINE_TUPLE

    adv_iterable = AdvancedIterator(zero_to_nine_generator())
    assert tuple(reversed(adv_iterable)) == ZERO_TO_NINE_TUPLE[::-1]

    adv_iterable = AdvancedIterator(zero_to_nine_generator())
    assert tuple(reversed(reversed(adv_iterable))) == ZERO_TO_NINE_TUPLE

    adv_iterable = AdvancedIterator(zero_to_nine_generator())
    assert tuple(reversed(reversed(reversed(adv_iterable)))) == ZERO_TO_NINE_TUPLE[::-1]

    adv_iterable = AdvancedIterator(zero_to_nine_generator())
    assert tuple(reversed(reversed(reversed(reversed(adv_iterable))))) == ZERO_TO_NINE_TUPLE


def test_advanced_iterator_reverse_slice_reverse():
    adv_iterable = AdvancedIterator(zero_to_nine_generator(), reversed_source=reversed(ZERO_TO_NINE_TUPLE))
    assert tuple(reversed(reversed(adv_iterable)[2:5])) == (5, 6, 7)

    adv_iterable = AdvancedIterator(zero_to_nine_generator())
    assert tuple(reversed(reversed(adv_iterable)[2:5])) == (5, 6, 7)


def test_advanced_iterator_slice_reverse_slice():
    adv_iterable = AdvancedIterator(zero_to_nine_generator(), reversed_source=reversed(ZERO_TO_NINE_TUPLE))
    assert tuple(reversed(adv_iterable[1:8])[2:5]) == (5, 4, 3)

    adv_iterable = AdvancedIterator(zero_to_nine_generator())
    assert tuple(reversed(adv_iterable[1:8])[2:5]) == (5, 4, 3)


def test_advanced_iterator_filter():
    iter_ = AdvancedIterator(zero_to_nine_generator())
    iter_.add_filter(lambda x: x >= 2)
    assert tuple(iter_) == (2, 3, 4, 5, 6, 7, 8, 9)

    iter_ = AdvancedIterator(zero_to_nine_generator())
    iter_.add_filter(lambda x: x % 2 == 0)
    assert tuple(iter_) == (0, 2, 4, 6, 8)


def test_advanced_iterator_filter_then_reverse():
    iter_ = AdvancedIterator(zero_to_nine_generator())
    iter_.add_filter(lambda x: x >= 2)
    assert tuple(reversed(iter_)) == (2, 3, 4, 5, 6, 7, 8, 9)[::-1]

    iter_ = AdvancedIterator(zero_to_nine_generator())
    iter_.add_filter(lambda x: x % 2 == 0)
    assert tuple(reversed(iter_)) == (0, 2, 4, 6, 8)[::-1]


def test_advanced_iterator_reverse_then_filter():
    iter_ = AdvancedIterator(zero_to_nine_generator())
    reversed_iter = reversed(iter_)
    reversed_iter.add_filter(lambda x: x >= 2)
    assert tuple(reversed_iter) == (2, 3, 4, 5, 6, 7, 8, 9)[::-1]

    iter_ = AdvancedIterator(zero_to_nine_generator())
    reversed_iter = reversed(iter_)
    reversed_iter.add_filter(lambda x: x % 2 == 0)
    assert tuple(reversed_iter) == (0, 2, 4, 6, 8)[::-1]


def test_advanced_iterator_filter_then_slice():
    iter_ = AdvancedIterator(zero_to_nine_generator())
    iter_.add_filter(lambda x: x >= 2)
    assert tuple(iter_[3:5]) == (2, 3, 4, 5, 6, 7, 8, 9)[3:5]

    iter_ = AdvancedIterator(zero_to_nine_generator())
    iter_.add_filter(lambda x: x % 2 == 0)
    assert tuple(iter_[3:5]) == (0, 2, 4, 6, 8)[3:5]


def test_advanced_iterator_slice_then_filter():
    iter_ = AdvancedIterator(zero_to_nine_generator())
    sliced = iter_[:5]
    sliced.add_filter(lambda x: x >= 2)
    assert tuple(sliced) == (2, 3, 4)

    iter_ = AdvancedIterator(zero_to_nine_generator())
    sliced = iter_[:5]
    sliced.add_filter(lambda x: x % 2 == 0)
    assert tuple(sliced) == (0, 2, 4)
