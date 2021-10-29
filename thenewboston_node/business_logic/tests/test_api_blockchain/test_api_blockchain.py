import pytest

from thenewboston_node.business_logic.blockchain.api_blockchain import APIBlockchain
from thenewboston_node.business_logic.tests.base import as_primary_validator, force_blockchain


@pytest.mark.usefixtures('node_mock_for_node_client')
def test_yield_nodes(node_client, file_blockchain_with_five_block_chunks, pv_network_address):
    with force_blockchain(file_blockchain_with_five_block_chunks), as_primary_validator():
        api_blockchain = APIBlockchain(network_address='http://testserver/')
        nodes = list(api_blockchain.yield_nodes())
        assert len(nodes) == 3
        assert {node.identifier for node in nodes} == {
            '0c838f7f50020ea586b2cd26b4f3cc7b5b399161af43e584f0cc3110952e3c05',
            'b9dc49411424cce606d27eeaa8d74cb84826d8a1001d17603638b73bdc6077f1',
            '1c8e5f54a15b63a9f3d540ce505fd0799575ffeaac62ce625c917e6d915ea8bb',
        }
