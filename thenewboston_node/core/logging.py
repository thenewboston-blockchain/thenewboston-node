import functools
import logging
from itertools import chain
from time import time

from .utils.misc import Default, upper_first

module_logger = logging.getLogger(__name__)
validation_logger = logging.getLogger(__name__ + '.validation')


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


def timeit_method(logger=module_logger, level=logging.DEBUG):
    return timeit(logger=logger, level=level, is_method=True)


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


class validates:

    def __init__(
        self,
        target_template,
        logger=validation_logger,
        level=logging.DEBUG,
        is_plural_target=False,
        use_format_map=False
    ):
        self.logger = logger
        self.level = level
        self.target_template = target_template
        self.is_plural_target = is_plural_target
        self.use_format_map = use_format_map

    def log_validation_started(self, target):
        self.logger.log(self.level, 'Validating %s', target)

    def log_validation_passed(self, target):
        self.logger.log(self.level, '%s %s valid', upper_first(target), 'are' if self.is_plural_target else 'is')

    def log_validation_failed(self, target, exception):
        self.logger.log(
            self.level, '%s %s invalid: %s', upper_first(target), 'are' if self.is_plural_target else 'is', exception
        )

    def __enter__(self):  # type: ignore
        self.log_validation_started(self.target_template)
        return self

    def __exit__(self, *exc_info) -> None:  # type: ignore
        if any(exc_info):
            self.log_validation_failed(self.target_template, exc_info[1])
        else:
            self.log_validation_passed(self.target_template)

    def __call__(self, callable_):

        @functools.wraps(callable_)
        def wrapper(*args, **kwargs):
            if self.use_format_map:
                target = self.target_template.format_map(Default(**kwargs))
            else:
                target = self.target_template.format(*args, **kwargs)
            self.log_validation_started(target)
            try:
                rv = callable_(*args, **kwargs)
            except Exception as ex:
                self.log_validation_failed(target, ex)
                raise
            else:
                self.log_validation_passed(target)
                return rv

        return wrapper
