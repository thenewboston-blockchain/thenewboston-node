from hashlib import sha3_256


def test_normalized_blockchain_state(blockchain_genesis_state):
    assert blockchain_genesis_state.get_normalized() == (
        b'{"message":'
        b'{"account_states":{"4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732":'
        b'{"balance":281474976710656},'
        b'"b9dc49411424cce606d27eeaa8d74cb84826d8a1001d17603638b73bdc6077f1":'
        b'{"node":{"fee_amount":4,"network_addresses":["http://localhost:8555/"]},'
        b'"primary_validator_schedule":{"begin_block_number":0,"end_block_number":99}}}},'
        b'"signer":"b9dc49411424cce606d27eeaa8d74cb84826d8a1001d17603638b73bdc6077f1"}'
    )


def test_get_next_block_identifier(blockchain_genesis_state):
    assert blockchain_genesis_state.next_block_identifier == sha3_256(
        b'{"account_states":{"4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732":'
        b'{"balance":281474976710656},'
        b'"b9dc49411424cce606d27eeaa8d74cb84826d8a1001d17603638b73bdc6077f1":'
        b'{"node":{"fee_amount":4,"network_addresses":["http://localhost:8555/"]},'
        b'"primary_validator_schedule":{"begin_block_number":0,"end_block_number":99}}}}'
    ).digest().hex()

    blockchain_genesis_state.next_block_identifier = 'next-block-identifier'
    assert blockchain_genesis_state.next_block_identifier == 'next-block-identifier'
