import pytest

from thenewboston_node.core.utils.retry import TryError, try_with_arguments


def divide(x, y):
    return x / y


@pytest.mark.parametrize('arguments', [
    [(100, 10)],
    [{
        'x': 100,
        'y': 10
    }],
])
def test_many_input_arguments(arguments):
    assert try_with_arguments(arguments, func=divide) == 10


def test_kwargs():
    assert try_with_arguments(arguments=[100], func=divide, kwargs={'y': 5}) == 20


def test_default_kwarg_is_overwritten():
    assert try_with_arguments([{'x': 100, 'y': 5}], func=divide, kwargs={'x': 5}) == 20


def test_first_successful_result_is_returned():
    assert try_with_arguments(arguments=[(100, 10), (100, 5)], func=divide) == 10


def test_error_is_suppressed():
    assert try_with_arguments(arguments=[(100, 0), (100, 5)], func=divide) == 20


def test_first_unsuppressed_exception_is_raised():
    with pytest.raises(TypeError):
        try_with_arguments([(100, 0), (100, None)], func=divide, exceptions=ZeroDivisionError)


def test_suppress_multiple_exceptions():
    assert try_with_arguments(
        arguments=[(100, 0), (100, None), (100, 5)],
        func=divide,
        exceptions=(ZeroDivisionError, TypeError),
    ) == 20


def test_raise_retry_error():
    with pytest.raises(TryError) as exc_info:
        try_with_arguments([(0, 0)], func=divide)

    original_exc = exc_info.value.__cause__
    assert isinstance(original_exc, ZeroDivisionError)
