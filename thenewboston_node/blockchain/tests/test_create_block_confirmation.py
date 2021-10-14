from rest_framework import status

from thenewboston_node.business_logic.models import Block, CoinTransferSignedChangeRequest
from thenewboston_node.business_logic.tests.base import force_blockchain

API_V1_BLOCK_CONFIRMATIONS_URL = '/api/v1/block-confirmations/'


def test_block_is_added_to_blockchain_on_block_confirmation_request(
    api_client, file_blockchain, user_account, treasury_account_key_pair, preferred_node, primary_validator_key_pair
):
    change_request = CoinTransferSignedChangeRequest.from_main_transaction(
        blockchain=file_blockchain,
        recipient=user_account,
        amount=99,
        signing_key=treasury_account_key_pair.private,
        node=preferred_node,
    )
    block = Block.create_from_signed_change_request(
        file_blockchain, change_request, primary_validator_key_pair.private
    )
    block_confirmation_data = {
        'block': block.serialize_to_dict(),
        'confirmation_signer': '00aa',
        'confirmation_signature': '00aa',
    }

    with force_blockchain(file_blockchain):
        response = api_client.post(API_V1_BLOCK_CONFIRMATIONS_URL, data=block_confirmation_data)

    assert response.status_code == status.HTTP_201_CREATED


def test_cannot_add_invalid_block_on_block_confirmation_request(
    api_client, file_blockchain, user_account, treasury_account_key_pair, preferred_node, primary_validator_key_pair
):
    change_request = CoinTransferSignedChangeRequest.from_main_transaction(
        blockchain=file_blockchain,
        recipient=user_account,
        amount=99,
        signing_key=treasury_account_key_pair.private,
        node=preferred_node,
    )
    block = Block.create_from_signed_change_request(
        file_blockchain, change_request, primary_validator_key_pair.private
    )
    block.message.block_number = 99
    block_confirmation_data = {
        'block': block.serialize_to_dict(),
        'confirmation_signer': '00aa',
        'confirmation_signature': '00aa',
    }

    with force_blockchain(file_blockchain):
        response = api_client.post(API_V1_BLOCK_CONFIRMATIONS_URL, data=block_confirmation_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'non_field_errors': ['Block number must be equal to next block number (== head block number + 1)']
    }
