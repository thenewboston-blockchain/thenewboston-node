import glob
import os
import shutil
import stat
from itertools import chain
from pathlib import Path

import pytest

from thenewboston_node.core.utils.os import chmod_quite, remove_quite


@pytest.fixture
def base_filename():
    return f'long-filename-for-testing-{os.getpid()}.bin'


@pytest.fixture
def optimized_filename():
    return f'l/o/n/g/f/i/l/e/long-filename-for-testing-{os.getpid()}.bin'


@pytest.fixture
def base_file_path(blockchain_path, base_filename):
    return str(blockchain_path / base_filename)


@pytest.fixture
def blockchain_directory():
    directory = f'/tmp/for-thenewboston-blockchain-testing-{os.getpid()}'
    try:
        os.makedirs(directory, exist_ok=True)
        yield directory
    finally:
        for dir_path, dir_names, filenames in os.walk(directory):
            for dir_name in dir_names:
                chmod_quite(os.path.join(dir_path, dir_name), 0o777)

            for filename in filenames:
                chmod_quite(os.path.join(dir_path, filename), 0o666)

        if os.path.isdir(directory):
            shutil.rmtree(directory)


@pytest.fixture
def blockchain_path(blockchain_directory):
    return Path(blockchain_directory)


@pytest.fixture
def optimized_file_path(blockchain_path, optimized_filename):
    optimized_file_path = str(blockchain_path / optimized_filename)
    try:
        yield optimized_file_path
    finally:
        for path in chain((optimized_file_path,), glob.glob(optimized_file_path + '.*')):
            chmod_quite(path, stat.S_IWOTH)
            remove_quite(path)


@pytest.fixture
def compressible_data():
    return b'A' * 10000


@pytest.fixture
def incompressible_data():
    return bytes(bytearray(range(256)))
