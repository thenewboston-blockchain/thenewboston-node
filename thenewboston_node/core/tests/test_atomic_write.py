import os
import stat

import pytest

from thenewboston_node.core.utils.atomic_write import atomic_write_append


def test_can_append_atomic_to_existing_file(tmp_path):
    tmp_file = tmp_path / 'testfile'

    tmp_file.write_text('Hello ')
    with atomic_write_append(tmp_file, mode='a') as f:
        f.write('world')

    assert tmp_file.read_text() == 'Hello world'


@pytest.mark.parametrize('mode,data', [
    ('a', 'test'),
    ('ab', b'test'),
    ('w', 'test'),
    ('wb', b'test'),
])
def test_can_write_atomic_to_non_existing_file(tmp_path, mode, data):
    tmp_file = tmp_path / 'testfile'

    with atomic_write_append(tmp_file, mode=mode) as f:
        f.write(data)
    written = tmp_file.read_bytes() if 'b' in mode else tmp_file.read_text()

    assert written == data


def test_file_is_not_appended_on_error(tmp_path):
    tmp_file = tmp_path / 'testfile'

    tmp_file.write_text('first\n')
    try:
        with atomic_write_append(tmp_file, mode='a') as f:
            f.write('second\n')
            1 / 0
    except ZeroDivisionError:
        pass

    assert tmp_file.read_text() == 'first\n'


def test_file_is_not_created_on_error(tmp_path):
    tmp_file = tmp_path / 'testfile'

    try:
        with atomic_write_append(tmp_file, mode='w') as f:
            f.write('test')
            1 / 0
    except ZeroDivisionError:
        pass

    assert not tmp_file.exists()


@pytest.mark.parametrize('mode', (0o777, 0o400, 0o644))
def test_new_file_permissions_are_set(tmp_path, mode):
    tmp_file = tmp_path / 'testfile'

    with atomic_write_append(tmp_file, 'w', create_perms=mode) as f:
        f.write('test')

    perms = os.stat(tmp_file).st_mode & 0o777
    assert perms == stat.S_IMODE(mode)


@pytest.mark.parametrize('mode', (0o777, 0o400, 0o644))
def test_appended_file_permissions_are_persisted(tmp_path, mode):
    tmp_file = tmp_path / 'testfile'

    tmp_file.write_text('test\n')
    os.chmod(tmp_file, mode)
    with atomic_write_append(tmp_file, 'a') as f:
        f.write('test')

    perms = os.stat(tmp_file).st_mode & 0o777
    assert perms == stat.S_IMODE(mode)
