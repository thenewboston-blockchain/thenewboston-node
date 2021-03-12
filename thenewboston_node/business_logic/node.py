from django.conf import settings


def get_signing_key() -> str:
    signing_key = settings.SIGNING_KEY
    assert signing_key is not NotImplemented
    return signing_key
