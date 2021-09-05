import logging
import os
import re
from pathlib import Path
from typing import Union

from .file_system import FileSystemStorage, strip_compression_extension

logger = logging.getLogger(__name__)

REMOVE_RE = re.compile(r'[^0-9a-z]')

DEFAULT_MAX_DEPTH = 8


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

    def __init__(self, base_path: Union[str, Path], max_depth=DEFAULT_MAX_DEPTH, **kwargs):
        super().__init__(base_path=base_path, **kwargs)
        self.max_depth = max_depth

    def save(self, file_path, binary_data: bytes, is_final=False):
        return super().save(self.get_optimized_path(file_path), binary_data, is_final=is_final)

    def load(self, file_path) -> bytes:
        return super().load(self.get_optimized_path(file_path))

    def append(self, file_path, binary_data: bytes, is_final=False):
        return super().append(self.get_optimized_path(file_path), binary_data, is_final=is_final)

    def finalize(self, file_path):
        return super().finalize(self.get_optimized_path(file_path))

    def is_finalized(self, file_path):
        return super().is_finalized(self.get_optimized_path(file_path))

    def list_directory(self, prefix=None, sort_direction=1):
        if sort_direction not in (1, -1, None):
            raise ValueError('sort_direction must be either of the values: 1, -1, None')

        directory_path = prefix or '.'
        generator = self._list_directory_generator(directory_path)
        if sort_direction is None:
            yield from generator
        else:
            yield from sorted(generator, reverse=sort_direction == -1)

    def move(self, source, destination):
        optimized_source = self.get_optimized_path(source)
        optimized_destination = self.get_optimized_path(destination)
        super().move(optimized_source, optimized_destination)

    def get_mtime(self, file_path):
        return super().get_mtime(self.get_optimized_path(file_path))

    def _list_directory_generator(self, directory_path):
        directory_path = self._get_absolute_path(directory_path)
        for dir_path, _, filenames in os.walk(directory_path):
            # TODO(dmu) HIGH: Refactor: PathOptimizedFileSystemStorage should know nothing about compression
            original_filenames = map(strip_compression_extension, filenames)
            unique_filenames = set(original_filenames)  # remove duplicated files after strip

            duplicates = len(filenames) - len(unique_filenames)
            if duplicates:
                logger.warning(f'Duplicated files found: {duplicates}')

            for filename in unique_filenames:
                file_path = os.path.join(dir_path, filename)

                path = os.path.join(directory_path, filename)
                expected_optimized_path = self.get_optimized_path(path)
                if file_path != expected_optimized_path:
                    logger.warning('Expected %s optimized path, but got %s', expected_optimized_path, file_path)
                    continue

                yield os.path.relpath(path, self.base_path)

    def get_optimized_path(self, filename):
        return make_optimized_file_path(filename, self.max_depth)

    def get_optimized_absolute_actual_path(self, filename) -> str:
        return self.get_actual_file_path(self.get_optimized_path(filename))
