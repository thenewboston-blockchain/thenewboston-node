import pytest

from thenewboston_node.business_logic.storages.decorators import OptimizedPathStorageDecorator


def test_can_save_to_optimized_path(storage_mock):
    storage = OptimizedPathStorageDecorator(storage_mock, max_depth=8)
    storage.save('parent/file.txt', b'test data')
    assert storage_mock.files == {'parent/f/i/l/e/file.txt': b'test data'}


def test_can_load_from_optimized_path(storage_mock):
    storage_mock.save('parent/f/i/l/e/file.txt', b'test data')
    storage = OptimizedPathStorageDecorator(storage_mock, max_depth=8)
    data = storage.load('parent/file.txt')
    assert data == b'test data'


def test_can_append_to_optimized_path(storage_mock):
    storage = OptimizedPathStorageDecorator(storage_mock, max_depth=8)
    storage.append('parent/file.txt', b'test data')
    assert storage_mock.files == {'parent/f/i/l/e/file.txt': b'test data'}


def test_can_finalize_to_optimized_path(storage_mock):
    storage = OptimizedPathStorageDecorator(storage_mock, max_depth=8)
    storage.finalize('parent/file.txt')
    assert storage_mock.finalized == {'parent/f/i/l/e/file.txt'}


@pytest.mark.parametrize(
    'expected_paths,sort_dir', [
        (['a.txt', 'ab.txt', 'z.txt'], 1),
        (['z.txt', 'ab.txt', 'a.txt'], -1),
    ]
)
def test_list_optimized_sorting_is_correct(storage_mock, expected_paths, sort_dir):
    storage_mock.files = {
        'a/a.txt': b'',
        'a/b/ab.txt': b'',
        'z/z.txt': b'',
    }
    storage = OptimizedPathStorageDecorator(storage_mock, max_depth=8)
    files = list(storage.list_directory('', sort_direction=sort_dir))
    assert files == expected_paths
