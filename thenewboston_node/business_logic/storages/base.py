from typing import Union


class Storage:

    def save(self, file_path, binary_data: bytes, is_final=False):
        raise NotImplementedError()

    def load(self, file_path) -> bytes:
        raise NotImplementedError()

    def append(self, file_path, binary_data: bytes, is_final=False):
        raise NotImplementedError()

    def finalize(self, file_path):
        raise NotImplementedError()

    def list_directory(self, directory_path, sort_direction: Union[int, None] = 1):
        raise NotImplementedError()


def sort_filenames(file_paths, sort_direction):
    if sort_direction not in (1, -1, None):
        raise ValueError('sort_direction must be either of the values: 1, -1, None')

    if sort_direction is not None:
        reverse = sort_direction == -1
        file_paths = sorted(file_paths, reverse=reverse)
    return file_paths
