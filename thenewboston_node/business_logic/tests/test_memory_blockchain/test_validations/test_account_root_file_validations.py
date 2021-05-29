import pytest

from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain
from thenewboston_node.business_logic.exceptions import ValidationError


@pytest.mark.usefixtures('forced_mock_network')
def test_validate_account_root_files_raises(forced_memory_blockchain: MemoryBlockchain,):
    blockchain = forced_memory_blockchain

    assert blockchain.account_root_files
    for balance in blockchain.account_root_files[0].accounts.values():
        balance.balance_lock = ''
    with pytest.raises(ValidationError, match='Account lock must be set'):
        blockchain.validate_account_root_files()

    blockchain.account_root_files = []
    with pytest.raises(ValidationError, match='Blockchain must contain at least one account root file'):
        blockchain.validate_account_root_files()


@pytest.mark.skip('Not implemented yet')
def test_validate_account_root_file_balances():
    raise NotImplementedError
