import pytest
from rest_framework import status

from thenewboston_node.business_logic.models import Block, NodeDeclarationSignedChangeRequest
from thenewboston_node.business_logic.tests.base import force_blockchain
from thenewboston_node.business_logic.utils.blockchain_state import make_blockchain_genesis_state

API_V1_BLOCKCHAIN_STATE_URL_PATTERN = '/api/v1/blockchain-states-meta/{block_number}/'


@pytest.mark.parametrize('block_number', (-2, 'invalid_id', 0, 999))
def test_invalid_block_number_returns_404(api_client, file_blockchain, block_number):
    with force_blockchain(file_blockchain):
        response = api_client.get(API_V1_BLOCKCHAIN_STATE_URL_PATTERN.format(block_number=block_number))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize('block_number', ('-1', 'null', 'genesis', ' null '))
def test_can_get_blockchain_genesis_state_meta(api_client, file_blockchain, blockchain_genesis_state, block_number):
    with force_blockchain(file_blockchain):
        response = api_client.get(API_V1_BLOCKCHAIN_STATE_URL_PATTERN.format(block_number=block_number))

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()

    assert response_json == {
        'last_block_number':
            blockchain_genesis_state.last_block_number,
        'url_path':
            '/blockchain/blockchain-states/0/0/0/0/0/0/0/0/0000000000000000000!-blockchain-state.msgpack',
        'urls': [
            'http://localhost:8555/blockchain/blockchain-states/0/0/0/0/0/0/0/0/0000000000000000000!-blockchain-state.msgpack'
        ]
    }


def test_blockchain_state_meta_block_number_is_inclusive(api_client, file_blockchain, preferred_node_key_pair):
    with force_blockchain(file_blockchain):
        request = NodeDeclarationSignedChangeRequest.create(
            network_addresses=[], fee_amount=3, signing_key=preferred_node_key_pair.private
        )
        block = Block.create_from_signed_change_request(
            file_blockchain,
            signed_change_request=request,
            pv_signing_key=preferred_node_key_pair.private,
        )
        file_blockchain.add_block(block)
        file_blockchain.snapshot_blockchain_state()

        block_number = file_blockchain.get_last_block_number()
        response = api_client.get(API_V1_BLOCKCHAIN_STATE_URL_PATTERN.format(block_number=block_number))

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['last_block_number'] == block_number


def test_blockchain_state_meta_urls_returns_400_if_node_undeclared(
    api_client, file_blockchain, treasury_account, treasury_initial_balance, another_node
):
    file_blockchain.clear()
    genesis_blockchain_state = make_blockchain_genesis_state(
        primary_validator=another_node,
        treasury_account_number=treasury_account,
        treasury_account_initial_balance=treasury_initial_balance,
    )
    file_blockchain.add_blockchain_state(genesis_blockchain_state)

    with force_blockchain(file_blockchain):
        response = api_client.get(API_V1_BLOCKCHAIN_STATE_URL_PATTERN.format(block_number=-1))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()

    assert data['detail'] == 'Requested node is unregistered in the blockchain'
