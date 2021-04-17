import gzip
import os.path
import stat
from os import stat as os_stat
from unittest.mock import patch

import pytest

from thenewboston_node.business_logic.storages.path_optimized_file_system import (
    PathOptimizedFileSystemStorage, make_optimized_file_path
)
from thenewboston_node.business_logic.tests.test_storages.utils import mkdir_and_touch


def test_make_optimized_file_path():
    assert make_optimized_file_path('a', 0) == 'a'
    assert make_optimized_file_path('a', 1) == 'a/a'
    assert make_optimized_file_path('a', 2) == 'a/a'
    assert make_optimized_file_path('a', 3) == 'a/a'

    assert make_optimized_file_path('a.json', 0) == 'a.json'
    assert make_optimized_file_path('a.json', 1) == 'a/a.json'
    assert make_optimized_file_path('a.json', 2) == 'a/a.json'
    assert make_optimized_file_path('a.json', 3) == 'a/a.json'

    assert make_optimized_file_path('d/a.json', 0) == 'd/a.json'
    assert make_optimized_file_path('d/a.json', 1) == 'd/a/a.json'
    assert make_optimized_file_path('d/a.json', 2) == 'd/a/a.json'
    assert make_optimized_file_path('d/a.json', 3) == 'd/a/a.json'

    assert make_optimized_file_path('/d/a.json', 0) == '/d/a.json'
    assert make_optimized_file_path('/d/a.json', 1) == '/d/a/a.json'
    assert make_optimized_file_path('/d/a.json', 2) == '/d/a/a.json'
    assert make_optimized_file_path('/d/a.json', 3) == '/d/a/a.json'

    assert make_optimized_file_path('/d/abc.json', 0) == '/d/abc.json'
    assert make_optimized_file_path('/d/abc.json', 1) == '/d/a/abc.json'
    assert make_optimized_file_path('/d/abc.json', 2) == '/d/a/b/abc.json'
    assert make_optimized_file_path('/d/abc.json', 3) == '/d/a/b/c/abc.json'

    assert make_optimized_file_path('/d/abc-def-ghi.json', 8) == '/d/a/b/c/d/e/f/g/h/abc-def-ghi.json'
    assert make_optimized_file_path('/d/abc-def ghi.json', 8) == '/d/a/b/c/d/e/f/g/h/abc-def ghi.json'
    assert make_optimized_file_path('/d/ABCDEFGHI.json', 8) == '/d/a/b/c/d/e/f/g/h/ABCDEFGHI.json'
    assert make_optimized_file_path('/d/12345abcd.json', 8) == '/d/1/2/3/4/5/a/b/c/12345abcd.json'


def test_can_save(base_file_path, optimized_file_path):
    fss = PathOptimizedFileSystemStorage()
    fss.save(base_file_path, b'\x08Test')
    assert os.path.isfile(optimized_file_path)
    with open(optimized_file_path, 'rb') as fo:
        assert fo.read() == b'\x08Test'


def test_can_save_finalize(base_file_path, optimized_file_path):
    fss = PathOptimizedFileSystemStorage()
    fss.save(base_file_path, b'\x08Test', is_final=True)
    assert os_stat(optimized_file_path).st_mode & (stat.S_IWGRP | stat.S_IWUSR | stat.S_IWOTH) == 0


def test_can_finalize(base_file_path, optimized_file_path):
    fss = PathOptimizedFileSystemStorage()
    fss.save(base_file_path, b'\x08Test')
    assert os_stat(optimized_file_path).st_mode & (stat.S_IWGRP | stat.S_IWUSR | stat.S_IWOTH) != 0

    fss.finalize(base_file_path)
    assert os_stat(optimized_file_path).st_mode & (stat.S_IWGRP | stat.S_IWUSR | stat.S_IWOTH) == 0


def test_can_append(base_file_path, optimized_file_path):
    fss = PathOptimizedFileSystemStorage()
    fss.save(base_file_path, b'\x08Test')
    assert os.path.isfile(optimized_file_path)
    with open(optimized_file_path, 'rb') as fo:
        assert fo.read() == b'\x08Test'

    fss.append(base_file_path, b'\x09\x0aAPPEND')
    with open(optimized_file_path, 'rb') as fo:
        assert fo.read() == b'\x08Test\x09\x0aAPPEND'


def test_can_load(base_file_path, optimized_file_path):
    binary_data = b'\x08Test'

    fss = PathOptimizedFileSystemStorage()
    fss.save(base_file_path, binary_data)
    assert os.path.isfile(optimized_file_path)
    with open(optimized_file_path, 'rb') as fo:
        assert fo.read() == binary_data

    assert fss.load(base_file_path) == binary_data


def test_compression(base_file_path, optimized_file_path):
    binary_data = b'A' * 10000

    fss = PathOptimizedFileSystemStorage(compressors=('gz',))
    fss.save(base_file_path, binary_data, is_final=True)
    expected_path = optimized_file_path + '.gz'
    assert os.path.isfile(expected_path)

    with gzip.open(expected_path, 'rb') as fo:
        assert fo.read() == binary_data

    assert fss.load(base_file_path) == binary_data


def test_list_directory(blockchain_directory):
    base_directory = os.path.join(blockchain_directory, 'test')

    fss = PathOptimizedFileSystemStorage(compressors=('gz',))
    fss.save(os.path.join(base_directory, '1434567890.txt'), b'A' * 1000, is_final=True)
    fss.save(os.path.join(base_directory, '1134567890.txt'), b'test1')
    fss.save(os.path.join(base_directory, '1234567890.txt'), b'test2')
    fss.save(os.path.join(base_directory, '1334567890.txt'), b'test3')

    assert {
        os.path.join(base_directory, '1134567890.txt'),
        os.path.join(base_directory, '1234567890.txt'),
        os.path.join(base_directory, '1334567890.txt'),
        os.path.join(base_directory, '1434567890.txt'),
    } == set(fss.list_directory(base_directory))


def test_can_save_to_optimized_path():
    storage = PathOptimizedFileSystemStorage()
    with patch('thenewboston_node.business_logic.storages.file_system.FileSystemStorage.save') as save_mock:
        storage.save('parent/file.txt', b'test data')

    save_mock.assert_called_once_with('parent/f/i/l/e/file.txt', b'test data', is_final=False)


def test_can_load_from_optimized_path():
    storage = PathOptimizedFileSystemStorage()
    with patch('thenewboston_node.business_logic.storages.file_system.FileSystemStorage.load') as load_mock:
        storage.load('parent/file.txt')

    load_mock.assert_called_once_with('parent/f/i/l/e/file.txt')


def test_can_append_to_optimized_path():
    storage = PathOptimizedFileSystemStorage()
    with patch('thenewboston_node.business_logic.storages.file_system.FileSystemStorage.append') as append_mock:
        storage.append('parent/file.txt', b'test data')

    append_mock.assert_called_once_with('parent/f/i/l/e/file.txt', b'test data', is_final=False)


def test_can_finalize_to_optimized_path():
    storage = PathOptimizedFileSystemStorage()
    with patch('thenewboston_node.business_logic.storages.file_system.FileSystemStorage._finalize') as finalize_mock:
        storage.finalize('parent/file.txt')

    finalize_mock.assert_called_once_with('parent/f/i/l/e/file.txt')


def test_list_optimized_sorting_is_correct():
    return_value = [
        ('a', ('b',), ('a.txt',)),
        ('a/b', (), ('ab.txt',)),
        ('z', (), ('z.txt',)),
    ]
    storage = PathOptimizedFileSystemStorage()

    with patch('os.walk') as os_walk_mock:
        os_walk_mock.return_value = return_value
        assert list(storage.list_directory('')) == ['a.txt', 'ab.txt', 'z.txt']

    with patch('os.walk') as os_walk_mock:
        os_walk_mock.return_value = return_value
        assert list(storage.list_directory('', -1)) == ['z.txt', 'ab.txt', 'a.txt']


@pytest.mark.parametrize(
    'sort_direction,expected', (
        (1, ('1.txt', '10.txt', '2.txt')),
        (-1, ('2.txt', '10.txt', '1.txt')),
    )
)
def test_can_list_directory_with_sorting(blockchain_path, sort_direction, expected):
    storage = PathOptimizedFileSystemStorage()
    expected_absolute = [str(blockchain_path / rel_path) for rel_path in expected]

    mkdir_and_touch(blockchain_path / '1/1.txt')
    mkdir_and_touch(blockchain_path / '1/0/10.txt')
    mkdir_and_touch(blockchain_path / '2/2.txt')

    listed = list(storage.list_directory(blockchain_path, sort_direction=sort_direction))
    assert listed == expected_absolute


def test_can_list_directory_without_sorting(blockchain_path):
    storage = PathOptimizedFileSystemStorage()

    mkdir_and_touch(blockchain_path / '1/1.txt')
    mkdir_and_touch(blockchain_path / '1/0/10.txt')
    mkdir_and_touch(blockchain_path / '2/2.txt')

    listed = storage.list_directory(blockchain_path, sort_direction=None)
    assert {
        str(blockchain_path / '1.txt'),
        str(blockchain_path / '10.txt'),
        str(blockchain_path / '2.txt'),
    } == set(listed)


@pytest.mark.parametrize('wrong_sort_direction', [2, -2, object(), 0, '1'])
def test_list_directory_validate_sort_direction(blockchain_directory, wrong_sort_direction):
    storage = PathOptimizedFileSystemStorage()
    with pytest.raises(ValueError):
        list(storage.list_directory(blockchain_directory, sort_direction=wrong_sort_direction))


def test_non_optimized_paths_are_not_listed(blockchain_path):
    storage = PathOptimizedFileSystemStorage()
    non_optimized_file_path = 'file.txt'

    mkdir_and_touch(blockchain_path / non_optimized_file_path)

    listed = list(storage.list_directory(blockchain_path))
    assert listed == []


@pytest.mark.parametrize('compression', ('gz', 'bz2', 'xz'))
def test_list_directory_strips_compression_extensions(blockchain_path, compression):
    storage = PathOptimizedFileSystemStorage()

    mkdir_and_touch(blockchain_path / f'a/a.txt.{compression}')

    listed = list(storage.list_directory(blockchain_path))
    assert listed == [str(blockchain_path / 'a.txt')]


def test_list_directory_filename_is_not_duplicated_on_name_conflict(blockchain_path):
    storage = PathOptimizedFileSystemStorage()

    mkdir_and_touch(blockchain_path / 'f/i/l/e/file.txt')
    mkdir_and_touch(blockchain_path / 'f/i/l/e/file.txt.gz')

    listed = list(storage.list_directory(blockchain_path))
    assert listed == [str(blockchain_path / 'file.txt')]


def test_move(blockchain_path):
    source = str(blockchain_path / 'file1.txt')
    destination = str(blockchain_path / 'file2.txt')

    storage = PathOptimizedFileSystemStorage(max_depth=5)
    storage.save(source, b'AAA')
    assert os.path.isfile(str(blockchain_path / 'f/i/l/e/1/file1.txt'))

    storage.move(source, destination)
    assert os.path.isfile(str(blockchain_path / 'f/i/l/e/2/file2.txt'))
    assert not os.path.isfile(str(blockchain_path / 'f/i/l/e/1/file1.txt'))
    assert storage.load(destination) == b'AAA'
