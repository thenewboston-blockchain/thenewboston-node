import json
from hashlib import sha3_256
from typing import NamedTuple

from nacl.exceptions import BadSignatureError
from nacl.signing import SigningKey, VerifyKey

from thenewboston_node.core.utils.misc import bytes_to_hex, hex_to_bytes
from thenewboston_node.core.utils.types import hexstr


class KeyPair(NamedTuple):
    public: hexstr
    private: hexstr


def generate_signature(signing_key: hexstr, message: bytes) -> hexstr:
    return SigningKey(hex_to_bytes(signing_key)).sign(message).signature.hex()


def derive_verify_key(signing_key: hexstr):
    return bytes_to_hex(SigningKey(hex_to_bytes(signing_key)).verify_key)


def is_signature_valid(verify_key: hexstr, message: bytes, signature: hexstr) -> bool:
    try:
        verify_key_bytes = hex_to_bytes(verify_key)
        signature_bytes = hex_to_bytes(signature)
    except ValueError:
        return False

    try:
        VerifyKey(verify_key_bytes).verify(message, signature_bytes)
    except BadSignatureError:
        return False

    return True


def normalize_dict(dict_: dict) -> bytes:
    return json.dumps(dict_, separators=(',', ':'), sort_keys=True).encode('utf-8')


def hash_normalized_dict(normalized_dict: bytes) -> hexstr:
    return hexstr(sha3_256(normalized_dict).digest().hex())


def generate_key_pair() -> KeyPair:
    signing_key = SigningKey.generate()
    return KeyPair(bytes_to_hex(signing_key.verify_key), bytes_to_hex(signing_key))
