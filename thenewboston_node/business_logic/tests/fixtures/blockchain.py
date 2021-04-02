import logging
import random
from unittest.mock import patch

from django.test import override_settings

import pytest
from tqdm import tqdm

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.blockchain.mock_blockchain import MockBlockchain
from thenewboston_node.business_logic.models.transfer_request import TransferRequest
from thenewboston_node.core.utils.cryptography import generate_key_pair

LARGE_MEMORY_BLOCKCHAIN_SIZE = 100

logger = logging.getLogger(__name__)


@pytest.fixture
def get_head_block_mock():
    with patch.object(MockBlockchain, 'get_head_block', return_value=None) as mock:
        yield mock


@pytest.fixture
def get_next_block_number_mock():
    with patch.object(MockBlockchain, 'get_next_block_number', return_value=0) as mock:
        yield mock


@pytest.fixture
def get_next_block_identifier_mock():
    with patch.object(MockBlockchain, 'get_next_block_identifier', return_value='next-block-identifier') as mock:
        yield mock


@pytest.fixture
def get_account_balance_mock():
    with patch.object(MockBlockchain, 'get_balance_value', return_value=430) as mock:
        yield mock


@pytest.fixture
def get_balance_lock_mock():
    with patch.object(MockBlockchain, 'get_balance_lock', return_value='fake-balance-lock') as mock:
        yield mock


@pytest.fixture
def forced_memory_blockchain(initial_account_root_file):
    blockchain_settings = {
        'class': 'thenewboston_node.business_logic.blockchain.memory_blockchain.MemoryBlockchain',
        'kwargs': {
            'initial_account_root_file': initial_account_root_file
        }
    }

    BlockchainBase.clear_instance_cache()
    with override_settings(BLOCKCHAIN=blockchain_settings):
        yield BlockchainBase.get_instance()
    BlockchainBase.clear_instance_cache()


@pytest.fixture
def forced_mock_blockchain(initial_account_root_file):
    blockchain_settings = {
        'class': 'thenewboston_node.business_logic.blockchain.mock_blockchain.MockBlockchain',
        'kwargs': {
            'initial_account_root_file': initial_account_root_file
        }
    }

    BlockchainBase.clear_instance_cache()
    with override_settings(BLOCKCHAIN=blockchain_settings):
        yield BlockchainBase.get_instance()
    BlockchainBase.clear_instance_cache()


@pytest.fixture
def large_memory_blockchain(forced_memory_blockchain, primary_validator, preferred_node, treasury_account_key_pair):
    blockchain = forced_memory_blockchain

    account_root_file = blockchain.get_first_account_root_file()
    accounts_with_balance = {account: balance.value for account, balance in account_root_file.accounts.items()}
    accounts = list(accounts_with_balance)

    assert len(accounts_with_balance) == 1
    assert treasury_account_key_pair.public in accounts_with_balance
    account_private_keys = {treasury_account_key_pair.public: treasury_account_key_pair.private}

    for _ in tqdm(range(LARGE_MEMORY_BLOCKCHAIN_SIZE)):
        for _ in range(1000):  # We do not use infinite loop on purpose (for safer code)
            amount = random.randint(1, 100)
            sender = random.choice(accounts)
            sender_balance_value = accounts_with_balance[sender]
            logger.debug('Chosen sender %s with balance value of %s', sender, sender_balance_value)
            total_amount = amount + primary_validator.fee_amount + preferred_node.fee_amount
            if sender_balance_value < total_amount:
                logger.debug('Chosen sender %s does not have enough funds', sender)
                continue

            sender_private_key = account_private_keys[sender]

            recipient = None
            if random.random() < 0.5:
                recipient = random.choice(accounts)
                if recipient == sender:
                    recipient = None

            if recipient is None:
                recipient_key_pair = generate_key_pair()
                recipient = recipient_key_pair.public
                accounts.append(recipient)
                account_private_keys[recipient] = recipient_key_pair.private

            transfer_request = TransferRequest.from_main_transaction(
                blockchain=blockchain,
                recipient=recipient,
                amount=amount,
                signing_key=sender_private_key,
                primary_validator=primary_validator,
                node=preferred_node
            )
            transfer_request.validate(blockchain)

            accounts_with_balance[sender] -= total_amount
            accounts_with_balance[recipient] = accounts_with_balance.get(recipient, 0) + amount
            break
        else:
            # We should never practically reach here
            raise Exception('Could not find an account with enough funds')

        blockchain.add_block_from_transfer_request(transfer_request)

    return blockchain
