from thenewboston_node.business_logic.models import Block, NodeDeclarationSignedChangeRequest


def test_create_node_declaration_block(memory_blockchain, user_account_key_pair):
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['127.0.0.1'],
        fee_amount=3,
        fee_account='fake_fee_account',
        signing_key=user_account_key_pair.private
    )
    block = Block.create_from_signed_change_request(memory_blockchain, request)
    assert block
    assert block.message.signed_change_request
    assert block.message.signed_change_request.signer
    assert block.message.signed_change_request.signature
    assert block.message.signed_change_request.message
    assert block.message.signed_change_request.message.node.network_addresses == ['127.0.0.1']
    assert block.message.signed_change_request.message.node.fee_amount == 3
    assert block.message.signed_change_request.message.node.fee_account == 'fake_fee_account'
