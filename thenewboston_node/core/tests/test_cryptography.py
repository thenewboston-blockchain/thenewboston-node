from thenewboston_node.core.utils.cryptography import derive_verify_key, generate_key_pair


def test_generate_key_pair():
    key_pair = generate_key_pair()
    assert isinstance(key_pair.private, str)
    assert len(key_pair.private) == 64
    assert isinstance(key_pair.public, str)
    assert len(key_pair.public) == 64

    derived_public = derive_verify_key(key_pair.private)
    assert derived_public == key_pair.public
    assert derived_public is not key_pair.public
