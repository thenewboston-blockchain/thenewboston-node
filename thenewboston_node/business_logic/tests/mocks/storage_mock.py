from thenewboston_node.business_logic.storages.base import Storage, sort_filenames


class StorageMock(Storage):

    def __init__(self):
        self.files = {}
        self.finalized = set()

    def save(self, file_path, binary_data: bytes, is_final=False):
        self.files[file_path] = binary_data

    def load(self, file_path) -> bytes:
        return self.files[file_path]

    def append(self, file_path, binary_data: bytes, is_final=False):
        self.files.setdefault(file_path, b'')
        self.files[file_path] += binary_data

    def finalize(self, file_path):
        self.finalized.add(file_path)

    def list_directory(self, directory_path, sort_direction=1):
        filenames = self.files.keys()
        filenames = filter(lambda s: s.startswith(directory_path), filenames)
        filenames = sort_filenames(filenames, sort_direction)
        return filenames
