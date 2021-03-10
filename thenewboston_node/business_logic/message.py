import json

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey


# We have `is_valid_message_signature()` as a function to reuse it in case of message structure change
# to be able to validate any legacy message
def is_valid_message_signature(key: str, message: bytes, signature: str) -> bool:
    try:
        key_bytes = bytes.fromhex(key)
        signature_bytes = bytes.fromhex(signature)
    except ValueError:
        return False

    try:
        VerifyKey(key_bytes).verify(message, signature_bytes)
    except BadSignatureError:
        return False

    return True


def make_signable_message(dict_: dict) -> bytes:
    return json.dumps(dict_, separators=(',', ':'), sort_keys=True).encode('utf-8')
