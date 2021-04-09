import gzip
import os.path
import stat
from os import stat as os_stat

from thenewboston_node.business_logic.storages.file_system import FileSystemStorage, make_optimized_file_path


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
    fss = FileSystemStorage()
    fss.save(base_file_path, b'\x08Test')
    assert os.path.isfile(optimized_file_path)
    with open(optimized_file_path, 'rb') as fo:
        assert fo.read() == b'\x08Test'


def test_can_save_finalize(base_file_path, optimized_file_path):
    fss = FileSystemStorage()
    fss.save(base_file_path, b'\x08Test', is_final=True)
    assert os_stat(optimized_file_path).st_mode & (stat.S_IWGRP | stat.S_IWUSR | stat.S_IWOTH) == 0


def test_can_finalize(base_file_path, optimized_file_path):
    fss = FileSystemStorage()
    fss.save(base_file_path, b'\x08Test')
    assert os_stat(optimized_file_path).st_mode & (stat.S_IWGRP | stat.S_IWUSR | stat.S_IWOTH) != 0

    fss.finalize(base_file_path)
    assert os_stat(optimized_file_path).st_mode & (stat.S_IWGRP | stat.S_IWUSR | stat.S_IWOTH) == 0


def test_can_append(base_file_path, optimized_file_path):
    fss = FileSystemStorage()
    fss.save(base_file_path, b'\x08Test')
    assert os.path.isfile(optimized_file_path)
    with open(optimized_file_path, 'rb') as fo:
        assert fo.read() == b'\x08Test'

    fss.append(base_file_path, b'\x09\x0aAPPEND')
    with open(optimized_file_path, 'rb') as fo:
        assert fo.read() == b'\x08Test\x09\x0aAPPEND'


def test_can_load(base_file_path, optimized_file_path):
    binary_data = b'\x08Test'

    fss = FileSystemStorage()
    fss.save(base_file_path, binary_data)
    assert os.path.isfile(optimized_file_path)
    with open(optimized_file_path, 'rb') as fo:
        assert fo.read() == binary_data

    assert fss.load(base_file_path) == binary_data


def test_compression(base_file_path, optimized_file_path):
    binary_data = b'A' * 10000

    fss = FileSystemStorage(compressors=('gz',))
    fss.save(base_file_path, binary_data, is_final=True)
    expected_path = optimized_file_path + '.gz'
    assert os.path.isfile(expected_path)

    with gzip.open(expected_path, 'rb') as fo:
        assert fo.read() == binary_data

    assert fss.load(base_file_path) == binary_data


def test_list_directory(blockchain_directory):
    base_directory = os.path.join(blockchain_directory, 'test')

    fss = FileSystemStorage(compressors=('gz',))
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
