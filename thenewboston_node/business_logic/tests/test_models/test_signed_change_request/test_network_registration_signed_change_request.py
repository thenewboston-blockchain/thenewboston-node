from thenewboston_node.business_logic.models import NodeDeclarationSignedChangeRequest


def test_can_create_network_registration_signed_change_request(user_account_key_pair):
    request = NodeDeclarationSignedChangeRequest.create(['127.0.0.1'], user_account_key_pair.private)
    assert request
    assert request.signer
    assert request.signature
    assert request.message
    assert request.message.network_addresses == ['127.0.0.1']
