import os.path

import pytest

from thenewboston_node.business_logic import exceptions
from thenewboston_node.business_logic.storages.file_system import FileSystemStorage
from thenewboston_node.business_logic.tests.test_storages.utils import compress, decompress


@pytest.mark.parametrize('compression', ('gz', 'bz2', 'xz'))
def test_can_load_compressed_file(blockchain_path, compression, compressible_data):
    fss = FileSystemStorage(blockchain_path)
    compressed_path = blockchain_path / f'file.txt.{compression}'

    compress(compressed_path, compression, compressible_data)

    loaded_data = fss.load('file.txt')
    assert loaded_data == compressible_data


@pytest.mark.parametrize('compression', ('gz', 'bz2', 'xz'))
def test_incompressible_data_is_saved_raw(blockchain_path, compression, incompressible_data):
    fss = FileSystemStorage(blockchain_path)
    file_path = blockchain_path / 'incompressible_file.txt'

    fss.save('incompressible_file.txt', binary_data=incompressible_data, is_final=True)

    assert file_path.exists()
    assert file_path.read_bytes() == incompressible_data


def test_no_compression_file_storage_saves_raw_files(blockchain_path, compressible_data):
    fss = FileSystemStorage(blockchain_path, compressors=())
    file_path = blockchain_path / 'file.txt'

    fss.save('file.txt', binary_data=compressible_data, is_final=True)

    assert file_path.exists()
    assert file_path.read_bytes() == compressible_data


@pytest.mark.parametrize('compression', ('gz', 'bz2', 'xz'))
def test_finalized_data_is_compressed(blockchain_path, compression, compressible_data):
    fss = FileSystemStorage(blockchain_path, compressors=(compression,))
    file_path = blockchain_path / f'file.txt.{compression}'

    fss.save('file.txt', compressible_data, is_final=True)

    decompressed_data = decompress(file_path, compression)
    assert decompressed_data == compressible_data


@pytest.mark.parametrize('is_final', (True, False))
def test_save_to_compressed_finalized_file_raises_error(
    blockchain_path, compressible_data, incompressible_data, is_final
):
    fss = FileSystemStorage(blockchain_path, compressors=('gz',))
    filename = 'file.txt'

    fss.save(filename, binary_data=compressible_data, is_final=True)

    with pytest.raises(exceptions.FinalizedFileWriteError):
        fss.save(filename, incompressible_data, is_final)


@pytest.mark.parametrize('is_final', (True, False))
def test_save_to_raw_finalized_file_raises_error(blockchain_path, compressible_data, is_final):
    fss = FileSystemStorage(blockchain_path, compressors=())
    filename = 'file.txt'

    fss.save(filename, binary_data=compressible_data, is_final=True)

    with pytest.raises(exceptions.FinalizedFileWriteError):
        fss.save(filename, compressible_data, is_final)


def test_best_compression_method_is_chosen(blockchain_path, compressible_data):
    fss = FileSystemStorage(blockchain_path, compressors=('gz', 'bz2', 'xz'))
    compressed_path = blockchain_path / 'file.txt.gz'

    fss.save('file.txt', binary_data=compressible_data, is_final=True)

    assert compressed_path.exists()
    assert len(compressed_path.read_bytes()) == 46


def test_load_finalized_file_on_name_conflict(blockchain_path):
    fss = FileSystemStorage(blockchain_path)
    non_finalized_file = blockchain_path / 'file.txt'
    finalized_file = blockchain_path / 'file.txt.gz'

    non_finalized_file.write_bytes(b'non finalized data')
    compress(finalized_file, compression='gz', binary_data=b'finalized data')

    loaded_data = fss.load(file_path='file.txt')
    assert loaded_data == b'finalized data'


def test_move(blockchain_path):
    fss = FileSystemStorage(blockchain_path)
    source = 'file1.txt'
    destination = 'file2.txt'

    fss.save(source, b'AAA')
    fss.move(source, destination)
    assert os.path.isfile(blockchain_path / destination)
    assert not os.path.isfile(blockchain_path / source)
    assert fss.load(destination) == b'AAA'


@pytest.mark.parametrize('is_final', (True, False))
def test_cannot_append_to_compressed_finalized_file(blockchain_path, compressible_data, is_final):
    fss = FileSystemStorage(blockchain_path, compressors=('gz',))
    filename = 'file.txt'

    fss.save(filename, binary_data=compressible_data, is_final=True)

    with pytest.raises(exceptions.FinalizedFileWriteError):
        fss.append(filename, b'appended data', is_final)


@pytest.mark.parametrize('is_final', (True, False))
def test_cannot_append_to_raw_finalized_file(blockchain_path, incompressible_data, is_final):
    fss = FileSystemStorage(blockchain_path, compressors=())
    filename = 'file.txt'

    fss.save(filename, binary_data=incompressible_data, is_final=True)

    with pytest.raises(exceptions.FinalizedFileWriteError):
        fss.append(filename, b'appended data', is_final)


def test_cannot_save_file_out_of_base_directory(blockchain_path, compressible_data):
    fss = FileSystemStorage(blockchain_path / 'subdir')
    file_path = '../file.txt'

    with pytest.raises(ValueError):
        fss.save(file_path, compressible_data)


def test_cannot_use_absolute_path(blockchain_path, compressible_data):
    fss = FileSystemStorage(blockchain_path)
    file_path = blockchain_path / 'subdir/file.txt'

    with pytest.raises(ValueError):
        fss.save(file_path, compressible_data)
