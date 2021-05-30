from thenewboston_node.business_logic.models import Block, NodeDeclarationSignedChangeRequest


def test_create_network_registration_block(memory_blockchain, user_account_key_pair):
    request = NodeDeclarationSignedChangeRequest.create(['127.0.0.1'], user_account_key_pair.private)
    block = Block.create_from_signed_change_request(memory_blockchain, request)
    assert block
    assert block.message.signed_change_request.message.network_addresses == ['127.0.0.1']
