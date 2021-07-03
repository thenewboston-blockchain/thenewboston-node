import pytest

from thenewboston_node.business_logic.models import Block, NodeDeclarationSignedChangeRequest
from thenewboston_node.business_logic.models.mixins.compactable import compact_key as ck
from thenewboston_node.business_logic.node import get_node_signing_key
from thenewboston_node.core.utils.types import hexstr


def test_create_node_declaration_block(memory_blockchain, user_account_key_pair):
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['127.0.0.1'],
        fee_amount=3,
        fee_account=hexstr('dcba'),
        signing_key=user_account_key_pair.private
    )
    block = Block.create_from_signed_change_request(memory_blockchain, request, get_node_signing_key())
    assert block
    assert block.message.signed_change_request
    assert block.message.signed_change_request.signer
    assert block.message.signed_change_request.signature
    assert block.message.signed_change_request.message
    assert block.message.signed_change_request.message.node.network_addresses == ['127.0.0.1']
    assert block.message.signed_change_request.message.node.fee_amount == 3
    assert block.message.signed_change_request.message.node.fee_account == hexstr('dcba')


def test_node_identifier_is_removed_when_node_declaration_signed_change_request_is_serialized(
    memory_blockchain, user_account_key_pair
):
    request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['127.0.0.1'],
        fee_amount=3,
        fee_account=hexstr('dcba'),
        signing_key=user_account_key_pair.private
    )
    block = Block.create_from_signed_change_request(memory_blockchain, request, get_node_signing_key())
    compact_dict = block.to_compact_dict()
    assert ck('identifier') not in compact_dict[ck('message')][ck('signed_change_request')][ck('message')][ck('node')]


@pytest.mark.skip('Not implemented yet')
def test_fee_account_key_is_removed_when_serialized_if_value_is_null():
    raise NotImplementedError


@pytest.mark.skip('Not implemented yet')
def test_fee_account_key_is_removed_when_serialized_if_value_is_equal_to_account_state():
    raise NotImplementedError
