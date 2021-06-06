from thenewboston_node.business_logic.models import NodeDeclarationSignedChangeRequest


def test_can_create_node_declaration_signed_change_request(user_account_key_pair):
    request = NodeDeclarationSignedChangeRequest.create(
        identifier='abcd',
        network_addresses=['127.0.0.1'],
        fee_amount=3,
        fee_account='fake_fee_account',
        signing_key=user_account_key_pair.private
    )
    assert request
    assert request.signer
    assert request.signature
    assert request.message
    assert request.message.node.network_addresses == ['127.0.0.1']
    assert request.message.node.fee_amount == 3
    assert request.message.node.fee_account == 'fake_fee_account'
