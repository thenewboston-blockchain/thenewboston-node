import json
from hashlib import sha3_256

from nacl.exceptions import BadSignatureError
from nacl.signing import SigningKey, VerifyKey

from thenewboston_node.core.utils.misc import bytes_to_hex, hex_to_bytes


def generate_signature(signing_key: str, message: bytes) -> str:
    return SigningKey(hex_to_bytes(signing_key)).sign(message).signature.hex()


def derive_verify_key(signing_key: str):
    return bytes_to_hex(SigningKey(hex_to_bytes(signing_key)).verify_key)


def is_signature_valid(verify_key: str, message: bytes, signature: str) -> bool:
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


def normalize_dict_message(message: dict) -> bytes:
    return json.dumps(message, separators=(',', ':'), sort_keys=True).encode('utf-8')


def hash_normalized_message(message: bytes) -> str:
    return sha3_256(message).digest().hex()


def generate_key_pair() -> tuple[str, str]:
    signing_key = SigningKey.generate()
    return bytes_to_hex(signing_key), bytes_to_hex(signing_key.verify_key)
