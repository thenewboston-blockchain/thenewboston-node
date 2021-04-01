def hex_to_bytes(hex_string: str) -> bytes:
    return bytes.fromhex(hex_string)


def bytes_to_hex(bytes_: bytes) -> str:
    return bytes(bytes_).hex()


def upper_first(string):
    # string.capitalize() also lowers all other letters, so we upper_first() function
    return string[:1].upper() + string[1:]
