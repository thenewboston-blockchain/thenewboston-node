from hashlib import sha3_256


def test_normalized_account_root_file(initial_account_root_file):
    assert initial_account_root_file.get_normalized() == (
        b'{"accounts":{"4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732":{'
        b'"lock":"4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732",'
        b'"value":281474976710656'
        b'}}}'
    )


def test_get_next_block_identifier(initial_account_root_file):
    assert initial_account_root_file.get_next_block_identifier() == sha3_256(
        b'{"accounts":{"4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732":{'
        b'"lock":"4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732",'
        b'"value":281474976710656'
        b'}}}'
    ).digest().hex()

    initial_account_root_file.next_block_identifier = 'next-block-identifier'
    assert initial_account_root_file.get_next_block_identifier() == 'next-block-identifier'
