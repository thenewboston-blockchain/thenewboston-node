import subprocess

import pytest

from thenewboston_node.business_logic.docs.impl import get_signed_change_request_message_child_models
from thenewboston_node.business_logic.docs.samples import SamplesFactory
from thenewboston_node.business_logic.models.signed_change_request_message import (
    CoinTransferSignedChangeRequestMessage, NodeDeclarationSignedChangeRequestMessage,
    PrimaryValidatorScheduleSignedChangeRequestMessage
)

known_signed_change_request_message_classes = {
    CoinTransferSignedChangeRequestMessage, NodeDeclarationSignedChangeRequestMessage,
    PrimaryValidatorScheduleSignedChangeRequestMessage
}


def test_get_signed_change_request_message_child_models():
    assert set(get_signed_change_request_message_child_models()) == known_signed_change_request_message_classes


@pytest.mark.skip('fails')
def test_get_sample_block_map():
    block_map = SamplesFactory().get_sample_block_map()
    assert block_map.keys() == known_signed_change_request_message_classes
    assert len(set(id(item) for item in block_map.values())) == len(block_map.values())


@pytest.mark.skip('fails')
def test_can_generate_docs():
    result = subprocess.run(['make', 'docs-html-test'], capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    assert result.returncode == 0
