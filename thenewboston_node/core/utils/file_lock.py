import functools

import filelock


def lock_method(lock_attr, exception):

    def decorator(f):

        @functools.wraps(f)
        def wrap(self, *args, **kwargs):
            lock = getattr(self, lock_attr)
            try:
                with lock:
                    return f(self, *args, **kwargs)
            except filelock.Timeout:
                raise exception

        return wrap

    return decorator


def ensure_locked(lock_attr, exception):

    def decorator(f):

        @functools.wraps(f)
        def wrap(self, *args, **kwargs):
            lock = getattr(self, lock_attr)
            if not lock.is_locked:
                raise exception

            return f(self, *args, **kwargs)

        return wrap

    return decorator
