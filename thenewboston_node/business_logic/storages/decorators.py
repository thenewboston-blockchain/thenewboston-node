import logging
import os
import re

from thenewboston_node.business_logic.storages.base import Storage, sort_filenames

logger = logging.getLogger(__name__)

REMOVE_RE = re.compile(r'[^0-9a-z]')


def make_optimized_file_path(path, max_depth):
    directory, filename = os.path.split(path)
    normalized_filename = REMOVE_RE.sub('', filename.rsplit('.', 1)[0].lower())
    extra_path = '/'.join(normalized_filename[:max_depth])
    return os.path.join(directory, extra_path, filename)


class OptimizedPathStorageDecorator(Storage):
    """
    Storage decorator transparently placing file to
    subdirectories (for file system performance reason)
    """

    def __init__(self, decorated_storage: Storage, max_depth=8):
        self.storage = decorated_storage
        self.max_depth = max_depth

    def save(self, file_path, binary_data: bytes, is_final=False):
        optimized_path = self._get_optimized_path(file_path)
        return self.storage.save(optimized_path, binary_data, is_final)

    def load(self, file_path) -> bytes:
        optimized_path = self._get_optimized_path(file_path)
        return self.storage.load(optimized_path)

    def append(self, file_path, binary_data: bytes, is_final=False):
        optimized_path = self._get_optimized_path(file_path)
        return self.storage.append(optimized_path, binary_data, is_final)

    def finalize(self, file_path):
        optimized_path = self._get_optimized_path(file_path)
        return self.storage.finalize(optimized_path)

    def list_directory(self, directory_path, sort_direction=1):
        optimized_paths = self.storage.list_directory(directory_path, sort_direction=None)
        normal_paths = self._map_to_non_optimized_paths(directory_path, optimized_paths)
        normal_paths = sort_filenames(normal_paths, sort_direction=sort_direction)
        return normal_paths

    def _get_optimized_path(self, file_path):
        return make_optimized_file_path(file_path, self.max_depth)

    def _map_to_non_optimized_paths(self, base_path, file_paths):
        for file_path in file_paths:
            basename = os.path.basename(file_path)
            path = os.path.join(base_path, basename)
            expected_optimized_path = self._get_optimized_path(path)
            if file_path != expected_optimized_path:
                logger.warning('Expected %s optimized path, but got %s', expected_optimized_path, file_path)
            else:
                yield path
