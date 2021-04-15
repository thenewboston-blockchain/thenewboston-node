import logging
import os
import re

from .file_system import FileSystemStorage, strip_compression_extension

logger = logging.getLogger(__name__)

REMOVE_RE = re.compile(r'[^0-9a-z]')


def make_optimized_file_path(path, max_depth):
    directory, filename = os.path.split(path)
    normalized_filename = REMOVE_RE.sub('', filename.rsplit('.', 1)[0].lower())
    extra_path = '/'.join(normalized_filename[:max_depth])
    return os.path.join(directory, extra_path, filename)


class PathOptimizedFileSystemStorage(FileSystemStorage):
    """
    Storage decorator transparently placing file to
    subdirectories (for file system performance reason)
    """

    def __init__(self, max_depth=8, **kwargs):
        super().__init__(**kwargs)
        self.max_depth = max_depth

    def save(self, file_path, binary_data: bytes, is_final=False):
        return super().save(self._get_optimized_path(file_path), binary_data, is_final=is_final)

    def load(self, file_path) -> bytes:
        return super().load(self._get_optimized_path(file_path))

    def append(self, file_path, binary_data: bytes, is_final=False):
        return super().append(self._get_optimized_path(file_path), binary_data, is_final=is_final)

    def finalize(self, file_path):
        return super().finalize(self._get_optimized_path(file_path))

    def list_directory(self, directory_path, sort_direction=1):
        if sort_direction not in (1, -1, None):
            raise ValueError('sort_direction must be either of the values: 1, -1, None')

        generator = self._list_directory_generator(directory_path)
        if sort_direction is None:
            yield from generator
        else:
            yield from sorted(generator, reverse=sort_direction == -1)

    def _list_directory_generator(self, directory_path):
        for dir_path, _, filenames in os.walk(directory_path):
            filenames = map(strip_compression_extension, filenames)
            filenames = set(filenames)  # remove duplicated files after strip
            for filename in filenames:
                file_path = os.path.join(dir_path, filename)

                path = os.path.join(directory_path, filename)
                expected_optimized_path = self._get_optimized_path(path)
                if file_path != expected_optimized_path:
                    logger.warning('Expected %s optimized path, but got %s', expected_optimized_path, file_path)
                    continue

                yield path

    def _get_optimized_path(self, file_path):
        return make_optimized_file_path(file_path, self.max_depth)
