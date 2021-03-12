def hex_to_bytes(hex_string: str) -> bytes:
    return bytes.fromhex(hex_string)


def bytes_to_hex(bytes_: bytes) -> str:
    return bytes(bytes_).hex()
