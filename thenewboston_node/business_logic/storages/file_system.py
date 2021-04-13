import bz2
import gzip
import logging
import lzma
import os
import stat

from thenewboston_node.business_logic.storages.base import Storage, sort_filenames
from thenewboston_node.business_logic.storages.decorators import OptimizedPathStorageDecorator
from thenewboston_node.core.logging import timeit_method

# TODO(dmu) LOW: Support more / better compression methods
COMPRESSION_FUNCTIONS = {
    'gz': lambda data: gzip.compress(data, compresslevel=9),
    'bz2': lambda data: bz2.compress(data, compresslevel=9),
    'xz': lzma.compress
}

DECOMPRESSION_FUNCTIONS = {
    'gz': gzip.decompress,
    'bz2': bz2.decompress,
    'xz': lzma.decompress,
}

logger = logging.getLogger(__name__)


def drop_write_permissions(filename):
    current_mode = os.stat(filename).st_mode
    mode = current_mode - (current_mode & (stat.S_IWGRP | stat.S_IWUSR | stat.S_IWOTH))
    os.chmod(filename, mode)


def strip_compression_extension(filename):
    for compressor in DECOMPRESSION_FUNCTIONS:
        if filename.endswith('.' + compressor):
            filename = filename[:-len(compressor) - 1]
            break
    return filename


def walk_directory(directory_path):
    for dir_path, _, filenames in os.walk(directory_path):
        for filename in filenames:
            yield os.path.join(dir_path, filename)


class FileSystemStorage(Storage):
    """
    Compressing / decompressing storage for capacity optimization
    """

    def __init__(self, compressors=tuple(COMPRESSION_FUNCTIONS)):
        self.compressors = compressors

    @timeit_method()
    def save(self, file_path, binary_data: bytes, is_final=False):
        self._persist(file_path, binary_data, 'wb', is_final=is_final)

    def load(self, file_path) -> bytes:
        for decompressor, func in DECOMPRESSION_FUNCTIONS.items():
            path = file_path + '.' + decompressor
            try:
                with open(path, mode='rb') as fo:
                    data = fo.read()
            except OSError:
                continue

            return func(data)  # type: ignore

        with open(file_path, mode='rb') as fo:
            return fo.read()

    def append(self, file_path, binary_data: bytes, is_final=False):
        self._persist(file_path, binary_data, 'ab', is_final=is_final)

    def finalize(self, file_path):
        new_filename = self._compress(file_path)
        drop_write_permissions(new_filename)

    def list_directory(self, directory_path, sort_direction=1):
        file_paths = walk_directory(directory_path)
        file_paths = map(strip_compression_extension, file_paths)
        file_paths = sort_filenames(file_paths, sort_direction)
        return file_paths

    @timeit_method()
    def _compress(self, file_path) -> str:
        compressors = self.compressors
        if not compressors:
            return file_path

        with open(file_path, 'rb') as fo:
            original_data = fo.read()

        logger.debug('File %s size: %s bytes', file_path, len(original_data))
        best_filename = file_path
        best_data = original_data

        for compressor in self.compressors:
            compress_function = COMPRESSION_FUNCTIONS[compressor]
            compressed_data = compress_function(original_data)  # type: ignore
            compressed_size = len(compressed_data)
            logger.debug(
                'File %s compressed with %s size: %s bytes (%.2f ratio)', file_path, compressor, compressed_size,
                compressed_size / len(original_data)
            )
            # TODO(dmu) LOW: For compressed_size == best[0] choose fastest compression
            if compressed_size < len(best_data):
                best_filename = file_path + '.' + compressor
                best_data = compressed_data
                logger.debug('New best %s: %s size', best_filename, len(best_data))

        if best_filename != file_path:
            logger.debug('Writing compressed file: %s (%s bytes)', best_filename, len(best_data))
            with open(best_filename, 'wb') as fo:
                fo.write(best_data)

            logger.debug('Removing %s', file_path)
            os.remove(file_path)

        return best_filename

    def _persist(self, file_path, binary_data: bytes, mode, is_final=False):
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        # TODO(dmu) HIGH: Optimize for 'wb' mode so we do not need to reread the file from
        #                 filesystem to compress it
        with open(file_path, mode=mode) as fo:
            fo.write(binary_data)

        if is_final:
            self.finalize(file_path)


def get_filesystem_storage(max_depth=8, compressors=tuple(COMPRESSION_FUNCTIONS)):
    """
    Storage transparently placing file to subdirectories (for file system performance reason) and
    compressing / decompressing them for storage capacity optimization
    """

    fs_storage = FileSystemStorage(compressors=compressors)
    optimized_fs_storage = OptimizedPathStorageDecorator(fs_storage, max_depth=max_depth)
    return optimized_fs_storage
