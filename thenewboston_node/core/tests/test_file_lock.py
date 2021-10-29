import multiprocessing
import tempfile
import threading

import pytest
from filelock import FileLock

from thenewboston_node.core.utils.file_lock import ensure_locked, lock_method


class LockedException(Exception):
    pass


class UnLockedException(Exception):
    pass


class Example:

    def __init__(self, filename, notify_event=None, wait_event=None):
        self.lock = FileLock(filename, timeout=0)
        self.notify_event = notify_event
        self.wait_event = wait_event

    @lock_method(lock_attr='lock', exception=LockedException())
    def locked_method(self):
        if self.notify_event:
            self.notify_event.set()

        if self.wait_event:
            self.wait_event.wait(timeout=1)

    @lock_method(lock_attr='lock', exception=LockedException())
    def reentrant_lock_method(self):
        self.locked_method()

    @ensure_locked(lock_attr='lock', exception=UnLockedException())
    def unlocked_method(self):
        pass


def test_file_lock_is_exclusive_for_threads():
    lock_filename = tempfile.mktemp()
    notify_event = threading.Event()
    wait_event = threading.Event()

    thread = threading.Thread(target=lambda: Example(lock_filename, notify_event, wait_event).locked_method())
    thread.start()

    notify_event.wait(timeout=1)
    with pytest.raises(LockedException):
        Example(lock_filename).locked_method()

    wait_event.set()
    thread.join()


def get_locked_method(lock_filename, notify_event, wait_event):
    return Example(lock_filename, notify_event, wait_event).locked_method()


def test_file_lock_is_exclusive_for_processes():
    lock_filename = tempfile.mktemp()
    notify_event = multiprocessing.Event()
    wait_event = multiprocessing.Event()

    process = multiprocessing.Process(target=get_locked_method, args=(lock_filename, notify_event, wait_event))
    process.start()

    notify_event.wait(timeout=1)
    with pytest.raises(LockedException):
        Example(lock_filename).locked_method()

    wait_event.set()
    process.join()


def test_file_lock_is_reentrant():
    filename = tempfile.mktemp()
    Example(filename).reentrant_lock_method()


def test_ensure_locked_decorator_raises_error():
    filename = tempfile.mktemp()
    obj = Example(filename)

    with pytest.raises(UnLockedException):
        obj.unlocked_method()
