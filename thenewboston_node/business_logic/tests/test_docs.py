from thenewboston_node.business_logic.docs.impl import get_signed_change_request_message_child_models
from thenewboston_node.business_logic.models.signed_change_request_message import (
    CoinTransferSignedChangeRequestMessage, NodeDeclarationSignedChangeRequestMessage
)


def test_get_signed_change_request_message_child_models():
    assert set(get_signed_change_request_message_child_models()
               ) == {CoinTransferSignedChangeRequestMessage, NodeDeclarationSignedChangeRequestMessage}
