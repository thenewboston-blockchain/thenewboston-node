import functools
import logging
import threading
from time import time

thread_local = threading.local()
thread_local.timeit_start = {}

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


class timeit:

    def __init__(
        self,
        name=None,
        logger=module_logger,
        level=logging.DEBUG,
    ):
        self.logger = logger
        self.level = level
        self.name = name

    def __enter__(self):
        thread_local.timeit_start[self] = time()
        self.logger.log(self.level, 'Started %s', self.name)
        return self

    def __exit__(self, *exc_info):
        duration_ms = (time() - thread_local.timeit_start[self]) * 1000
        if any(exc_info):
            self.logger.exception('Exception with %s in %.3fms', self.name, duration_ms)
        else:
            self.logger.log(self.level, 'Finished %s in %.3fms', self.name, duration_ms)

    def __call__(self, callable_):
        if self.name is None:
            self.name = callable_.__name__ + '()'

        @functools.wraps(callable_)
        def wrapper(*args, **kwargs):
            with self:
                return callable_(*args, **kwargs)

        return wrapper
