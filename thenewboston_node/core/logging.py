import functools
import logging
from itertools import chain
from time import time

module_logger = logging.getLogger(__name__)


class SentryFilter(logging.Filter):

    def filter(self, record):  # noqa: A003
        if record.levelno >= logging.WARNING and getattr(record, 'exc_info', None) is None:
            # TODO(dmu) MEDIUM: This hack leads to "NoneType: None" being printed along with
            #                   warning messages. Figure out a better solution.
            record.exc_info = (None, None, None)  # trigger Sentry to dump stack trace

        return True


# This class in `sentry` module because it is required for attaching `SentryFilter`
class FilteringNullHandler(logging.NullHandler):

    def handle(self, record):
        return self.filter(record)


def verbose_timeit_method(logger=module_logger, level=logging.DEBUG):
    return timeit(logger=logger, level=level, verbose=True, is_method=True)


def timeit(
    logger=module_logger,
    level=logging.DEBUG,
    verbose=False,
    verbose_args=False,
    verbose_return_value=False,
    is_method=False
):

    def decorator(callable_):

        @functools.wraps(callable_)
        def wrapper(*args, **kwargs):
            callable_name = callable_.__name__
            if is_method:
                obj = args[0]
                callable_name = '<{} object at {:#x}>.{}'.format(obj.__class__.__name__, id(obj), callable_name)

            if verbose or verbose_args:
                args_ = args[1:] if is_method else args
                args_repr = ', '.join(chain(map(repr, args_), (f'{key}={value!r}' for key, value in kwargs.items())))
            else:
                args_repr = '...'

            call_spec = f'{callable_name}({args_repr})'
            logger.log(level, 'Calling %s', call_spec)
            start = time()
            try:
                rv = callable_(*args, **kwargs)
            except Exception:
                duration_ms = (time() - start) * 1000
                logger.exception('Exception in %s after %.3fms', call_spec, duration_ms)
                raise
            else:
                duration_ms = (time() - start) * 1000
                if verbose or verbose_return_value:
                    logger.log(level, 'Returned %r from %s in %.3fms', rv, call_spec, duration_ms)
                else:
                    logger.log(level, 'Returned from %s in %.3fms', call_spec, duration_ms)

                return rv

        return wrapper

    return decorator
