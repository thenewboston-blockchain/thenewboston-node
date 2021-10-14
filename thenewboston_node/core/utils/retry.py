import logging
from typing import Callable, Iterable, Tuple, Type, Union

logger = logging.getLogger(__name__)

BaseExceptionType = Type[BaseException]


class TryError(Exception):
    pass


def try_with_arguments(
    arguments: Iterable,
    func: Callable,
    exceptions: Union[BaseExceptionType, Tuple[BaseExceptionType, ...]] = Exception,
    kwargs=None
):
    kwargs = kwargs or {}
    last_exc = None
    for args in arguments:
        try:
            if isinstance(args, dict):
                return func(**(kwargs | args))
            elif isinstance(args, (tuple, list)):
                return func(*args, **kwargs)
            else:
                return func(args, **kwargs)
        except exceptions as e:
            last_exc = e
            logger.info('Suppressed exception %s', e)

    if last_exc:
        raise TryError('All attempts failed') from last_exc
