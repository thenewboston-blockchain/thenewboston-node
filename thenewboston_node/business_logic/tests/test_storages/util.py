from pathlib import Path, PurePath
from typing import Union

from thenewboston_node.business_logic.storages.file_system import COMPRESSION_FUNCTIONS, DECOMPRESSION_FUNCTIONS


def mkdir_and_touch(filename):
    file_path = Path(filename)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.touch()


def compress(file_path: Union[str, PurePath], compression: str, binary_data: bytes):
    compression_func = COMPRESSION_FUNCTIONS[compression]
    file_path = Path(file_path)
    compressed_bytes = compression_func(binary_data)  # type: ignore
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(compressed_bytes)


def decompress(file_path: Union[str, PurePath], compression: str):
    decompression_func = DECOMPRESSION_FUNCTIONS[compression]
    file_path = Path(file_path)
    compressed_bytes = file_path.read_bytes()
    return decompression_func(compressed_bytes)  # type: ignore
