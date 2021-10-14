import pytest
from rest_framework import status

from thenewboston_node.blockchain.models.pending_block import PendingBlock
from thenewboston_node.business_logic.tests.baker_factories import make_coin_transfer_block

API_V1_BLOCKS_URL = '/api/v1/blocks/'


@pytest.mark.django_db
def test_can_create_pending_block(api_client):
    block = make_coin_transfer_block()
    block_dict = block.serialize_to_dict()

    response = api_client.post(API_V1_BLOCKS_URL, data=block_dict)

    assert response.status_code == status.HTTP_202_ACCEPTED
    pending_block = PendingBlock.objects.get(block_number=block.get_block_number(), block_hash=block.hash)
    assert pending_block.block == block_dict


@pytest.mark.django_db
def test_create_pending_block_api_is_idempotent(api_client):
    block = make_coin_transfer_block()
    _, created = PendingBlock.objects.get_or_create_for_block(block)
    assert created

    response = api_client.post(API_V1_BLOCKS_URL, data=block.serialize_to_dict())

    assert response.status_code == status.HTTP_202_ACCEPTED
