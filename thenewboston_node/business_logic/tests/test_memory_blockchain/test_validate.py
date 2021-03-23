import pytest

from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain
from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.core.utils.cryptography import KeyPair


@pytest.mark.skip('Not implemented yet')
@pytest.mark.usefixtures('forced_mock_network', 'get_primary_validator_mock', 'get_preferred_node_mock')
def test_can_validate_blockchain(
    forced_memory_blockchain: MemoryBlockchain,
    treasury_account_key_pair: KeyPair,
    user_account_key_pair: KeyPair,
    primary_validator_key_pair: KeyPair,
    node_key_pair: KeyPair,
):
    blockchain = forced_memory_blockchain
    blockchain.validate()

    raise NotImplementedError()


@pytest.mark.usefixtures('forced_mock_network')
def test_validate_account_root_files_raises(forced_memory_blockchain: MemoryBlockchain,):
    blockchain = forced_memory_blockchain

    assert blockchain.account_root_files
    for balance in blockchain.account_root_files[0].accounts.values():
        balance.balance_lock = ''
    with pytest.raises(ValidationError, match='Balance lock must be set'):
        blockchain.validate_account_root_files()

    blockchain.account_root_files = []
    with pytest.raises(ValidationError, match='Blockchain must contain at least one account root file'):
        blockchain.validate_account_root_files()


@pytest.mark.skip('Not implemented yet')
def test_can_validate_blockchain_in_chunks():
    raise NotImplementedError()
