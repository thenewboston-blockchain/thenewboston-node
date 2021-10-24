from unittest.mock import patch

import pytest
from rest_framework import status

from thenewboston_node.blockchain.models.pending_block import PendingBlock
from thenewboston_node.business_logic.models import Block
from thenewboston_node.business_logic.tests.baker_factories import make_coin_transfer_block
from thenewboston_node.business_logic.tests.base import as_confirmation_validator, force_blockchain

API_V1_BLOCKS_URL = '/api/v1/blocks/'


@pytest.mark.django_db
def test_post_api_v1_blocks(
    api_client, file_blockchain, user_account_key_pair, preferred_node, start_send_block_confirmations_mock
):
    blockchain = file_blockchain
    block = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account_key_pair.public,
        amount=10,
        request_signing_key=blockchain._test_treasury_account_key_pair.private,
        pv_signing_key=blockchain._test_primary_validator_key_pair.private,
        preferred_node=preferred_node,
    )
    block_dict = block.serialize_to_dict()

    with force_blockchain(blockchain), as_confirmation_validator():
        response = api_client.post(API_V1_BLOCKS_URL, data=block_dict)

    assert response.status_code == status.HTTP_202_ACCEPTED
    start_send_block_confirmations_mock.assert_called_once()

    pending_block = PendingBlock.objects.get(block_number=block.get_block_number(), block_hash=block.hash)
    assert pending_block.block == block_dict


@pytest.mark.django_db
@pytest.mark.usefixtures('node_mock_for_node_client')
def test_post_api_v1_blocks_integration(api_client, file_blockchain, user_account_key_pair, preferred_node):
    blockchain = file_blockchain
    block = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account_key_pair.public,
        amount=10,
        request_signing_key=blockchain._test_treasury_account_key_pair.private,
        pv_signing_key=blockchain._test_primary_validator_key_pair.private,
        preferred_node=preferred_node,
    )
    block_dict = block.serialize_to_dict()

    with force_blockchain(blockchain), as_confirmation_validator():
        with patch(
            'thenewboston_node.blockchain.views.'
            'block_confirmation.BlockConfirmationViewSet.perform_create'
        ) as perform_create_mock:
            response = api_client.post(API_V1_BLOCKS_URL, data=block_dict)

    assert response.status_code == status.HTTP_202_ACCEPTED
    perform_create_mock.assert_called_once()

    calls = perform_create_mock.call_args_list
    assert len(calls) == 1
    call = calls[0]
    assert call[0][0].validated_data['block'].get_block_number() == block.get_block_number()
    assert call[0][0].validated_data['block'].hash == block.hash


@pytest.mark.django_db
def test_create_pending_block_api_is_idempotent(api_client):
    block = make_coin_transfer_block()
    _, is_created = PendingBlock.objects.get_or_create_for_block(block)
    assert is_created

    response = api_client.post(API_V1_BLOCKS_URL, data=block.serialize_to_dict())
    assert response.status_code == status.HTTP_202_ACCEPTED
