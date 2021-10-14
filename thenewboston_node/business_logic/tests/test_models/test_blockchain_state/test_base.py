from hashlib import sha3_256


def test_normalized_blockchain_state(blockchain_genesis_state):
    assert blockchain_genesis_state.message.get_normalized_for_cryptography() == (
        b'{"account_states":{"0c838f7f50020ea586b2cd26b4f3cc7b5b399161af43e584f0cc3110952e3c05":'
        b'{"node":{"fee_amount":1,"network_addresses":["http://cv.non-existing-domain:8555/"]},"'
        b'primary_validator_schedule":{"begin_block_number":100,"end_block_number":199}},'
        b'"1c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bb":{"node":{"fee_amount":1,'
        b'"network_addresses":["http://preferred-node.non-existing-domain:8555/"]}},'
        b'"4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732":{"balance":281474976710656},'
        b'"b9dc49411424cce606d27eeaa8d74cb84826d8a1001d17603638b73bdc6077f1":{"node":{"fee_amount":4,'
        b'"network_addresses":["http://pv.non-existing-domain:8555/"]},"primary_validator_schedule":'
        b'{"begin_block_number":0,"end_block_number":99}}}}'
    )


def test_get_next_block_identifier(blockchain_genesis_state):

    assert blockchain_genesis_state.next_block_identifier == sha3_256(
        b'{"account_states":{"0c838f7f50020ea586b2cd26b4f3cc7b5b399161af43e584f0cc3110952e3c05":'
        b'{"node":{"fee_amount":1,"network_addresses":["http://cv.non-existing-domain:8555/"]},"'
        b'primary_validator_schedule":{"begin_block_number":100,"end_block_number":199}},'
        b'"1c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bb":{"node":{"fee_amount":1,'
        b'"network_addresses":["http://preferred-node.non-existing-domain:8555/"]}},'
        b'"4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732":{"balance":281474976710656},'
        b'"b9dc49411424cce606d27eeaa8d74cb84826d8a1001d17603638b73bdc6077f1":{"node":{"fee_amount":4,'
        b'"network_addresses":["http://pv.non-existing-domain:8555/"]},"primary_validator_schedule":'
        b'{"begin_block_number":0,"end_block_number":99}}}}'
    ).digest().hex()

    blockchain_genesis_state.next_block_identifier = 'next-block-identifier'
    assert blockchain_genesis_state.next_block_identifier == 'next-block-identifier'
