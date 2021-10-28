import pytest

from thenewboston_node.business_logic.blockchain.api_blockchain import APIBlockchain
from thenewboston_node.business_logic.tests.base import as_primary_validator, force_blockchain


@pytest.mark.usefixtures('node_mock_for_node_client')
def test_yield_nodes(node_client, file_blockchain_with_five_block_chunks, pv_network_address):
    with force_blockchain(file_blockchain_with_five_block_chunks), as_primary_validator():
        api_blockchain = APIBlockchain(network_address='http://testserver/')
        nodes = list(api_blockchain.yield_nodes())
        assert len(nodes) == 3
