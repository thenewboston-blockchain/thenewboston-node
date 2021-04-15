import pytest

from thenewboston_node.business_logic.storages import exceptions
from thenewboston_node.business_logic.storages.file_system import FileSystemStorage
from thenewboston_node.business_logic.tests.test_storages.util import compress, decompress


@pytest.mark.parametrize('compression', ('gz', 'bz2', 'xz'))
def test_can_load_compressed_file(blockchain_path, compression, compressible_data):
    fss = FileSystemStorage()
    compressed_path = blockchain_path / f'file.txt.{compression}'

    compress(compressed_path, compression, compressible_data)

    loaded_data = fss.load(str(blockchain_path / 'file.txt'))
    assert loaded_data == compressible_data


@pytest.mark.parametrize('compression', ('gz', 'bz2', 'xz'))
def test_incompressible_data_is_saved_raw(blockchain_path, compression, incompressible_data):
    fss = FileSystemStorage()
    file_path = blockchain_path / 'incompressible_file.txt'

    fss.save(str(file_path), binary_data=incompressible_data, is_final=True)

    assert file_path.exists()
    assert file_path.read_bytes() == incompressible_data


def test_no_compression_file_storage_saves_raw_files(blockchain_path, compressible_data):
    fss = FileSystemStorage(compressors=())
    file_path = blockchain_path / 'file.txt'

    fss.save(str(file_path), binary_data=compressible_data, is_final=True)

    assert file_path.exists()
    assert file_path.read_bytes() == compressible_data


@pytest.mark.parametrize('compression', ('gz', 'bz2', 'xz'))
def test_finalized_data_is_compressed(blockchain_path, compression, compressible_data):
    fss = FileSystemStorage(compressors=(compression,))
    file_path = blockchain_path / f'file.txt.{compression}'

    fss.save(str(blockchain_path / 'file.txt'), compressible_data, is_final=True)

    decompressed_data = decompress(file_path, compression)
    assert decompressed_data == compressible_data


@pytest.mark.parametrize('is_final', (True, False))
def test_save_to_compressed_finalized_file_raises_error(
    blockchain_path, compressible_data, incompressible_data, is_final
):
    fss = FileSystemStorage(compressors=('gz',))
    file_path = str(blockchain_path / 'file.txt')

    fss.save(file_path, binary_data=compressible_data, is_final=True)

    with pytest.raises(exceptions.FinalizedFileWriteError):
        fss.save(file_path, incompressible_data, is_final)


@pytest.mark.parametrize('is_final', (True, False))
def test_save_to_raw_finalized_file_raises_error(blockchain_path, compressible_data, is_final):
    fss = FileSystemStorage(compressors=())
    file_path = str(blockchain_path / 'file.txt')

    fss.save(file_path, binary_data=compressible_data, is_final=True)

    with pytest.raises(exceptions.FinalizedFileWriteError):
        fss.save(file_path, compressible_data, is_final)


def test_best_compression_method_is_chosen(blockchain_path, compressible_data, incompressible_data):
    fss = FileSystemStorage(compressors=('gz', 'bz2', 'xz'))
    file_path = blockchain_path / 'file.txt'
    compressed_path = blockchain_path / 'file.txt.gz'

    fss.save(str(file_path), binary_data=compressible_data, is_final=True)

    assert compressed_path.exists()
    assert len(compressed_path.read_bytes()) == 46


def test_load_finalized_file_on_name_conflict(blockchain_path):
    fss = FileSystemStorage()
    non_finalized_file = blockchain_path / 'file.txt'
    finalized_file = blockchain_path / 'file.txt.gz'

    non_finalized_file.write_bytes(b'non finalized data')
    compress(finalized_file, compression='gz', binary_data=b'finalized data')

    loaded_data = fss.load(file_path=str(non_finalized_file))
    assert loaded_data == b'finalized data'
