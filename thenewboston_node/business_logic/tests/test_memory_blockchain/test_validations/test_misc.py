import pytest

from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain
from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.core.utils.cryptography import KeyPair


@pytest.mark.usefixtures('forced_mock_network', 'get_primary_validator_mock', 'get_preferred_node_mock')
def test_can_validate_blockchain(
    forced_memory_blockchain: MemoryBlockchain,
    treasury_account_key_pair: KeyPair,
    user_account_key_pair: KeyPair,
):
    user_account = user_account_key_pair.public
    treasury_account = treasury_account_key_pair.public

    blockchain = forced_memory_blockchain
    blockchain.validate(is_partial_allowed=False)

    block0 = Block.from_main_transaction(blockchain, user_account, 30, signing_key=treasury_account_key_pair.private)
    blockchain.add_block(block0)
    blockchain.make_account_root_file()
    blockchain.validate(is_partial_allowed=False)

    block1 = Block.from_main_transaction(blockchain, user_account, 10, signing_key=treasury_account_key_pair.private)
    blockchain.add_block(block1)
    blockchain.make_account_root_file()
    blockchain.validate(is_partial_allowed=False)

    block2 = Block.from_main_transaction(blockchain, treasury_account, 5, signing_key=user_account_key_pair.private)
    blockchain.add_block(block2)
    blockchain.make_account_root_file()
    blockchain.validate(is_partial_allowed=False)


@pytest.mark.skip('Not implemented yet')
def test_can_validate_blockchain_in_chunks():
    raise NotImplementedError()
