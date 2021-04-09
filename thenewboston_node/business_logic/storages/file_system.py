import bz2
import gzip
import logging
import lzma
import os
import os.path
import re
import stat

from thenewboston_node.core.logging import timeit_method

REMOVE_RE = re.compile(r'[^0-9a-z]')

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


def make_optimized_file_path(path, max_depth):
    directory, filename = os.path.split(path)
    normalized_filename = REMOVE_RE.sub('', filename.rsplit('.', 1)[0].lower())
    extra_path = '/'.join(normalized_filename[:max_depth])
    return os.path.join(directory, extra_path, filename)


def drop_write_permissions(filename):
    current_mode = os.stat(filename).st_mode
    mode = current_mode - (current_mode & (stat.S_IWGRP | stat.S_IWUSR | stat.S_IWOTH))
    os.chmod(filename, mode)


class FileSystemStorage:
    """
    Storage transparently placing file to subdirectories (for file system performance reason) and
    compressing / decompressing them for storage capacity optimization
    """

    def __init__(self, max_depth=8, compressors=tuple(COMPRESSION_FUNCTIONS)):
        self.max_depth = max_depth
        self.compressors = compressors

    def get_optimized_path(self, file_path):
        return make_optimized_file_path(file_path, self.max_depth)

    @timeit_method()
    def save(self, file_path, binary_data: bytes, is_final=False):
        self._persist(file_path, binary_data, 'wb', is_final=is_final)

    def load(self, file_path) -> bytes:
        optimized_path = self.get_optimized_path(file_path)
        for decompressor, func in DECOMPRESSION_FUNCTIONS.items():
            path = optimized_path + '.' + decompressor
            try:
                with open(path, mode='rb') as fo:
                    data = fo.read()
            except OSError:
                continue

            return func(data)  # type: ignore

        with open(optimized_path, mode='rb') as fo:
            return fo.read()

    def append(self, file_path, binary_data: bytes, is_final=False):
        self._persist(file_path, binary_data, 'ab', is_final=is_final)

    def finalize(self, file_path):
        optimized_path = self.get_optimized_path(file_path)
        new_filename = self._compress(optimized_path)
        drop_write_permissions(new_filename)

    def list_directory(self, directory_path):
        for dir_path, _, filenames in os.walk(directory_path):
            for filename in filenames:
                for compressor in DECOMPRESSION_FUNCTIONS:
                    if filename.endswith('.' + compressor):
                        filename = filename[:-len(compressor) - 1]
                        break

                proposed_optimized_path = os.path.join(dir_path, filename)
                path = os.path.join(directory_path, filename)
                expected_optimized_path = self.get_optimized_path(path)
                if proposed_optimized_path != expected_optimized_path:
                    logger.warning(
                        'Expected %s optimized path, but got %s', expected_optimized_path, proposed_optimized_path
                    )
                    continue

                yield path

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
        optimized_path = self.get_optimized_path(file_path)
        directory = os.path.dirname(optimized_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        # TODO(dmu) HIGH: Optimize for 'wb' mode so we do not need to reread the file from
        #                 filesystem to compress it
        with open(optimized_path, mode=mode) as fo:
            fo.write(binary_data)

        if is_final:
            self.finalize(file_path)
