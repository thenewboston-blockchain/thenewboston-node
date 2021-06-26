class hexstr(str):

    def to_bytes(self):
        return bytes.fromhex(self)

    @classmethod
    def from_bytes(cls, bytes_):
        return cls(bytes_.hex())
