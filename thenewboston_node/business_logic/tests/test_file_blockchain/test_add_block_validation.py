import pytest

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models import (
    Block, NodeDeclarationSignedChangeRequest, PrimaryValidatorScheduleSignedChangeRequest
)


def test_pv_schedule_after_node_declaration_is_successful(
    file_blockchain, another_node_key_pair, primary_validator_key_pair
):
    nd_request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://localhost:8555'],
        fee_amount=3,
        signing_key=another_node_key_pair.private,
    )
    nd_block = Block.create_from_signed_change_request(file_blockchain, nd_request, primary_validator_key_pair.private)
    file_blockchain.add_block(nd_block)

    pv_schedule_request = PrimaryValidatorScheduleSignedChangeRequest.create(
        begin_block_number=100,
        end_block_number=199,
        signing_key=another_node_key_pair.private,
    )
    pv_schedule_block = Block.create_from_signed_change_request(
        file_blockchain, pv_schedule_request, primary_validator_key_pair.private
    )
    file_blockchain.add_block(pv_schedule_block)

    file_blockchain.validate()


def test_pv_schedule_without_node_declaration_fails(
    file_blockchain, another_node_key_pair, primary_validator_key_pair
):
    pv_schedule_request = PrimaryValidatorScheduleSignedChangeRequest.create(
        begin_block_number=100,
        end_block_number=199,
        signing_key=another_node_key_pair.private,
    )
    pv_schedule_block = Block.create_from_signed_change_request(
        file_blockchain, pv_schedule_request, primary_validator_key_pair.private
    )

    with pytest.raises(
        ValidationError, match='Signer node must be declared in the blockchain before primary validator schedule'
    ):
        file_blockchain.add_block(pv_schedule_block)


def test_pv_schedule_begin_block_number_must_be_less_than_end_block_number(
    file_blockchain, another_node_key_pair, primary_validator_key_pair
):
    nd_request = NodeDeclarationSignedChangeRequest.create(
        network_addresses=['http://localhost:8555'],
        fee_amount=3,
        signing_key=another_node_key_pair.private,
    )
    nd_block = Block.create_from_signed_change_request(file_blockchain, nd_request, primary_validator_key_pair.private)
    file_blockchain.add_block(nd_block)

    pv_schedule_request = PrimaryValidatorScheduleSignedChangeRequest.create(
        begin_block_number=100,
        end_block_number=99,
        signing_key=another_node_key_pair.private,
    )
    pv_schedule_block = Block.create_from_signed_change_request(
        file_blockchain, pv_schedule_request, primary_validator_key_pair.private
    )

    with pytest.raises(ValidationError, match='Begin block number must be less or equal than end block number'):
        file_blockchain.add_block(pv_schedule_block)
