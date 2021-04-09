import pytest

from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain


@pytest.mark.skip('Not implemented yet')
@pytest.mark.usefixtures('forced_mock_network', 'get_primary_validator_mock', 'get_preferred_node_mock')
def test_can_add_block(blockchain_directory,):
    blockchain = FileBlockchain(blockchain_directory)
    assert blockchain
