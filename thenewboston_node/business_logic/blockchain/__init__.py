from .file_blockchain import file_blockchain


# TODO(dmu) MEDIUM: Make blockchain implementation configurable with settings
def get_blockchain():
    return file_blockchain
