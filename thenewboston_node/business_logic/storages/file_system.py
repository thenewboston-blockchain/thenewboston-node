import bz2
import gzip
import logging
import lzma
import os
import stat

from thenewboston_node.business_logic.storages import exceptions
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

STAT_WRITE_PERMS_ALL = stat.S_IWGRP | stat.S_IWUSR | stat.S_IWOTH

logger = logging.getLogger(__name__)


def drop_write_permissions(filename):
    current_mode = os.stat(filename).st_mode
    mode = current_mode - (current_mode & STAT_WRITE_PERMS_ALL)
    os.chmod(filename, mode)


def has_write_permissions(filename):
    current_mode = os.stat(filename).st_mode
    mode = current_mode & STAT_WRITE_PERMS_ALL
    return bool(mode)


def strip_compression_extension(filename):
    for compressor in DECOMPRESSION_FUNCTIONS:
        if filename.endswith('.' + compressor):
            return filename[:-len(compressor) - 1]

    return filename


def exist_compressed_file(file_path):
    for decompressor in DECOMPRESSION_FUNCTIONS:
        path = file_path + '.' + decompressor
        if os.path.exists(path):
            return True
    return False


class FileSystemStorage:
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
        self._finalize(file_path)

    def list_directory(self, directory_path, sort_direction=1):
        # TODO(dmu) HIGH: Implement it to list only current directory to be consitent with other methods
        #                     that are intended to operate on a give directory without nesting
        raise NotImplementedError

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
            self._write_file(best_filename, best_data, mode='wb')

            logger.debug('Removing %s', file_path)
            os.remove(file_path)

        return best_filename

    def _persist(self, file_path, binary_data: bytes, mode, is_final=False):
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        # TODO(dmu) HIGH: Optimize for 'wb' mode so we do not need to reread the file from
        #                 filesystem to compress it
        self._write_file(file_path, binary_data, mode)

        if is_final:
            self._finalize(file_path)

    def _finalize(self, file_path):
        new_filename = self._compress(file_path)
        drop_write_permissions(new_filename)

    def _is_finalized(self, file_path):
        return (
            exist_compressed_file(file_path) or (os.path.exists(file_path) and not has_write_permissions(file_path))
        )

    def _write_file(self, file_path, binary_data: bytes, mode):
        if self._is_finalized(file_path):
            raise exceptions.FinalizedFileWriteError(f"File is finalized '{file_path}'")

        with open(file_path, mode=mode) as fo:
            fo.write(binary_data)
