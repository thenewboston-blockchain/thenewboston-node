import bz2
import gzip
import logging
import lzma
import os
import re
import shutil
import stat
from functools import partial
from pathlib import Path
from typing import Optional, Union

from thenewboston_node.business_logic import exceptions
from thenewboston_node.core.logging import timeit_method
from thenewboston_node.core.utils.atomic_write import atomic_write_append

# TODO(dmu) LOW: Support more / better compression methods
COMPRESSION_FUNCTIONS = {
    'xz': lzma.compress,
    'bz2': lambda data: bz2.compress(data, compresslevel=9),
    'gz': lambda data: gzip.compress(data, compresslevel=9),
}

DECOMPRESSION_FUNCTIONS = {
    'xz': lzma.decompress,
    'bz2': bz2.decompress,
    'gz': gzip.decompress,
}

FILE_PATH_RE = re.compile(r'.*\.(?P<compressor>{})$'.format('|'.join(DECOMPRESSION_FUNCTIONS)))
STAT_WRITE_PERMS_ALL = stat.S_IWGRP | stat.S_IWUSR | stat.S_IWOTH

logger = logging.getLogger(__name__)


def ensure_directory_exists_for_file_path(file_path):
    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def drop_write_permissions(filename):
    current_mode = os.stat(filename).st_mode
    mode = current_mode - (current_mode & STAT_WRITE_PERMS_ALL)
    os.chmod(filename, mode)


def has_write_permissions(filename):
    return bool(os.stat(filename).st_mode & STAT_WRITE_PERMS_ALL)


def strip_compression_extension(filename):
    for compressor in DECOMPRESSION_FUNCTIONS:
        if filename.endswith('.' + compressor):
            return filename[:-len(compressor) - 1]

    return filename


open_read_binary = partial(open, mode='rb')


def get_compressor(file_path):
    match = FILE_PATH_RE.match(file_path)
    return match.group('compressor') if match else None


def read_compressed_file(file_path,
                         compressor=None,
                         raise_uncompressed_missing=True,
                         open_function=open_read_binary) -> Optional[bytes]:
    if compressor is None:
        compressor = get_compressor(file_path)
    elif compressor:  # we use empty line ('') to denote no compression
        file_path += '.' + compressor

    try:
        with open_function(file_path) as fo:
            data = fo.read()
    except OSError:
        if compressor is None and raise_uncompressed_missing:
            raise

        return None

    decompress_func = DECOMPRESSION_FUNCTIONS.get(compressor) or (lambda x: x)
    return decompress_func(data)  # type: ignore


class FileSystemStorage:
    """
    Compressing / decompressing storage for capacity optimization
    """

    def __init__(self, base_path: Union[str, Path], compressors=tuple(COMPRESSION_FUNCTIONS), temp_dir='.tmp'):
        self.base_path = Path(base_path).resolve()
        self.compressors = compressors
        self.temp_dir = self.base_path / temp_dir

    def clear(self):
        shutil.rmtree(self.base_path, ignore_errors=True)

    @timeit_method()
    def save(self, file_path: Union[str, Path], binary_data: bytes, is_final=False):
        self._persist(file_path, binary_data, 'wb', is_final=is_final)

    def load(self, file_path: Union[str, Path]) -> bytes:
        actual_file_path = self.get_actual_file_path(file_path)
        data = read_compressed_file(actual_file_path)
        if data is None:
            raise IOError(f'Could not read data from {actual_file_path} ({file_path})')

        return data

    def append(self, file_path: Union[str, Path], binary_data: bytes, is_final=False):
        self._persist(file_path, binary_data, 'ab', is_final=is_final)

    def finalize(self, file_path: Union[str, Path]):
        return self._finalize(self._get_absolute_path(file_path))

    def list_directory(self, prefix=None, sort_direction=1):
        # TODO(dmu) HIGH: Implement it to list only current directory to be consistent with other methods
        #                 that are intended to operate on a give directory without nesting
        raise NotImplementedError

    def move(self, source: Union[str, Path], destination: Union[str, Path]):
        source = self._get_absolute_path(source)
        destination = self._get_absolute_path(destination)
        ensure_directory_exists_for_file_path(destination)
        os.rename(source, destination)

    def get_mtime(self, file_path):
        return os.path.getmtime(self.get_actual_file_path(file_path))

    def is_finalized(self, file_path: Union[str, Path]):
        return self._is_finalized(self.get_actual_file_path(file_path))

    def _get_absolute_path(self, file_path: Union[str, Path]) -> Path:
        base_path = self.base_path
        path = Path(file_path)
        abs_path = (base_path / path).resolve()

        if path.is_absolute():
            raise ValueError(f"Cannot use absolute path: '{path}'")

        if not abs_path.is_relative_to(base_path):
            raise ValueError(f"Path '{abs_path}' is not relative to '{base_path}'")

        return abs_path

    @staticmethod
    def _get_compressed_file_path(absolute_path, prefer_uncompressed=False):
        # TODO(dmu) HIGH: Should we prefer uncompressed in case of existence of both versions?
        if prefer_uncompressed and os.path.exists(absolute_path):  # Fast track
            return absolute_path

        for decompressor in DECOMPRESSION_FUNCTIONS:
            compressed_absolute_path = absolute_path + '.' + decompressor
            if os.path.exists(compressed_absolute_path):
                return compressed_absolute_path

        return absolute_path

    def get_actual_file_path(self, file_path: Union[str, Path]) -> str:
        return self._get_compressed_file_path(str(self._get_absolute_path(file_path)))

    @timeit_method()
    def _compress(self, absolute_file_path: Path) -> Path:
        compressors = self.compressors
        if not compressors:  # Fast track
            return absolute_file_path

        with open(absolute_file_path, 'rb') as fo:
            original_data = fo.read()

        logger.debug('File %s size: %s bytes', absolute_file_path, len(original_data))
        best_absolute_file_path = absolute_file_path
        best_data = original_data

        for compressor in self.compressors:
            compress_function = COMPRESSION_FUNCTIONS[compressor]
            compressed_data = compress_function(original_data)  # type: ignore
            compressed_size = len(compressed_data)
            logger.debug(
                'File %s compressed with %s size: %s bytes (%.2f ratio)', absolute_file_path, compressor,
                compressed_size, compressed_size / len(original_data)
            )
            # TODO(dmu) LOW: For compressed_size == best[0] choose fastest compression
            if compressed_size < len(best_data):
                best_absolute_file_path = Path(str(absolute_file_path) + '.' + compressor)
                best_data = compressed_data
                logger.debug('New best %s: %s size', best_absolute_file_path, len(best_data))

        if best_absolute_file_path != absolute_file_path:
            logger.debug('Writing compressed file: %s (%s bytes)', best_absolute_file_path, len(best_data))
            self._write_file(best_absolute_file_path, best_data, mode='wb')

            logger.debug('Removing %s', absolute_file_path)
            os.remove(absolute_file_path)

        return best_absolute_file_path

    def _persist(self, file_path: Union[str, Path], binary_data: bytes, mode, is_final=False):
        absolute_file_path = self._get_absolute_path(file_path)
        ensure_directory_exists_for_file_path(str(absolute_file_path))

        # TODO(dmu) HIGH: Optimize for 'wb' mode so we do not need to reread the file from
        #                 filesystem to compress it
        self._write_file(absolute_file_path, binary_data, mode)

        if is_final:
            self._finalize(absolute_file_path)

    def _finalize(self, absolute_file_path: Path):
        actual_file_path = self._compress(absolute_file_path)
        drop_write_permissions(actual_file_path)
        return actual_file_path

    def _is_finalized(self, actual_file_path):
        return os.path.exists(actual_file_path) and not has_write_permissions(actual_file_path)

    def _write_file(self, absolute_file_path: Path, binary_data: bytes, mode):
        compressed_file_path = self._get_compressed_file_path(str(absolute_file_path))
        if self._is_finalized(compressed_file_path):
            raise exceptions.FinalizedFileWriteError(
                f'Could not write to file {absolute_file_path} finalized as {compressed_file_path}'
            )

        self.temp_dir.mkdir(parents=True, exist_ok=True)
        with atomic_write_append(absolute_file_path, mode=mode, dir=self.temp_dir) as fo:
            fo.write(binary_data)
