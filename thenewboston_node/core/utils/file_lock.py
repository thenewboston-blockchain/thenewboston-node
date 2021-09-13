import functools

import filelock

DEFAULT = object()


def lock_method(lock_attr, exception):

    def decorator(f):

        @functools.wraps(f)
        def wrap(self, *args, **kwargs):
            lock = getattr(self, lock_attr)
            lock_cache = getattr(self, '_lock_cache', None)
            try:
                with lock:
                    if lock_cache:
                        lock_cache.clear()
                    rv = f(self, *args, **kwargs)
            except filelock.Timeout:
                raise exception
            finally:
                if lock_cache:
                    lock_cache.clear()

            return rv

        return wrap

    return decorator


def lock_cached(method):

    @functools.wraps(method)
    def wrap(self, *args, **kwargs):
        key = (method, args, tuple(kwargs.items()))
        lock_cache = self._lock_cache
        value = lock_cache.get(key, DEFAULT)
        if value is DEFAULT:
            lock_cache[key] = value = method(self, *args, **kwargs)

        return value

    return wrap


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
