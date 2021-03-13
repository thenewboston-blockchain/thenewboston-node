from thenewboston_node.core.utils.cryptography import derive_verify_key, generate_key_pair


def test_generate_key_pair():
    private, public = generate_key_pair()
    assert isinstance(private, str)
    assert len(private) == 64
    assert isinstance(public, str)
    assert len(public) == 64

    derived_private = derive_verify_key(private)
    assert derived_private == public
    assert derived_private is not public
