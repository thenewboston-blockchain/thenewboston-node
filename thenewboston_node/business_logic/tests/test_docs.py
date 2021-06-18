from thenewboston_node.business_logic.docs.impl import get_signed_change_request_message_child_models
from thenewboston_node.business_logic.docs.samples import SamplesFactory
from thenewboston_node.business_logic.models.signed_change_request_message import (
    CoinTransferSignedChangeRequestMessage, NodeDeclarationSignedChangeRequestMessage
)

known_signed_change_request_message_classes = {
    CoinTransferSignedChangeRequestMessage, NodeDeclarationSignedChangeRequestMessage
}


def test_get_signed_change_request_message_child_models():
    assert set(get_signed_change_request_message_child_models()) == known_signed_change_request_message_classes


def test_get_sample_block_map():
    block_map = SamplesFactory().get_sample_block_map()
    assert block_map.keys() == known_signed_change_request_message_classes
    assert len(set(id(item) for item in block_map.values())) == len(block_map.values())
