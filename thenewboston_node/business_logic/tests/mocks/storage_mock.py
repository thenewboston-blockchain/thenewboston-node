class StorageMock:

    def __init__(self):
        self.files = {}
        self.finalized = set()

    def save(self, file_path, binary_data: bytes, is_final=False):
        self.files[file_path] = binary_data
        if is_final:
            self.finalize(file_path)

    def load(self, file_path) -> bytes:
        return self.files[file_path]

    def append(self, file_path, binary_data: bytes, is_final=False):
        self.files.setdefault(file_path, b'')
        self.files[file_path] += binary_data
        if is_final:
            self.finalize(file_path)

    def finalize(self, file_path):
        self.finalized.add(file_path)

    def list_directory(self, prefix=None, sort_direction=1):
        filenames = self.files.keys()
        if prefix:
            filenames = filter(lambda s: s.startswith(prefix), filenames)
        if sort_direction:
            reverse = True if sort_direction == -1 else False
            filenames = sorted(filenames, reverse=reverse)
        return filenames

    def move(self, source, destination):
        self.files[destination] = self.files.pop(source)

    def is_finalized(self, file_path):
        return file_path in self.finalized
