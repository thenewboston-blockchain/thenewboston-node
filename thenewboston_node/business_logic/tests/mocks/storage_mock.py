from collections import namedtuple
from time import time

File = namedtuple('File', 'content is_final mtime')


class StorageMock:

    def __init__(self):
        self.files = {}

    def save(self, file_path, binary_data: bytes, is_final=False):
        self.files[file_path] = File(content=binary_data, is_final=is_final, mtime=time())

    def load(self, file_path) -> bytes:
        return self.files[file_path].content

    def get_mtime(self, file_path):
        return self.files[file_path].mtime

    def append(self, file_path, binary_data: bytes, is_final=False):
        file = self.files.get(file_path) or File(content=b'', is_final=False, mtime=None)
        self.files[
            file_path
        ] = file._replace(  # type: ignore
            content=file.content + binary_data, is_final=is_final, mtime=time()
        )

    def finalize(self, file_path):
        self.files[file_path] = self.files[file_path]._replace(is_final=True, mtime=time())

    def list_directory(self, prefix=None, sort_direction=1):
        filenames = self.files.keys()
        if prefix:
            filenames = filter(lambda s: s.startswith(prefix), filenames)

        if sort_direction:
            filenames = sorted(filenames, reverse=sort_direction == -1)

        return filenames

    def move(self, source, destination):
        self.files[destination] = self.files.pop(source)

    def is_finalized(self, file_path):
        return self.files[file_path].is_final

    def get_optimized_path(self, file_path):
        return '0/0/0/0/' + file_path

    def get_optimized_actual_path(self, file_path):
        return '/tmp/safe-45745674567/' + self.get_optimized_path(file_path)
