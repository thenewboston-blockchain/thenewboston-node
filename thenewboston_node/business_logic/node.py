from django.conf import settings

from thenewboston_node.core.utils.cryptography import derive_verify_key


def get_node_signing_key() -> str:
    signing_key = settings.SIGNING_KEY
    assert signing_key is not NotImplemented
    return signing_key


# TODO(dmu) LOW: Cache get_node_identifier() function
def get_node_identifier() -> str:
    return derive_verify_key(get_node_signing_key())
