from datetime import datetime

from thenewboston_node.business_logic.models import (
    BlockchainStateMessage, CoinTransferSignedChangeRequest, CoinTransferSignedChangeRequestMessage,
    CoinTransferTransaction
)
from thenewboston_node.business_logic.models.account_state import AccountState
from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.business_logic.models.block_message import BlockMessage
from thenewboston_node.business_logic.models.blockchain_state import BlockchainState
from thenewboston_node.business_logic.node import get_node_signing_key
from thenewboston_node.business_logic.utils.blockchain import generate_blockchain
from thenewboston_node.core.utils.cryptography import KeyPair, derive_public_key
from thenewboston_node.core.utils.factory import Factory, factory
from thenewboston_node.core.utils.types import hexstr

DEFAULT_ACCOUNT = hexstr('d5356888dc9303e44ce52b1e06c3165a7759b9df1e6a6dfbd33ee1c3df1ab4d1')
PV_ACCOUNT = hexstr('dbc82ca874ae06ea39ea40f6f12dcca9c28aa88df989d9723338d7c9b941c0b1')

# TODO(dmu) HIGH: Replace these factories with `baker`-based factories


def add_blocks(blockchain, block_count, treasury_account_private_key=None, add_blockchain_genesis_state=False):
    if treasury_account_private_key:
        treasury_account_key_pair = KeyPair(
            public=derive_public_key(treasury_account_private_key), private=treasury_account_private_key
        )
    else:
        treasury_account_key_pair = blockchain._test_treasury_account_key_pair

    # TODO(dmu) HIGH: generate_blockchain() must call add blocks, not vice versa
    generate_blockchain(
        blockchain,
        block_count,
        get_node_signing_key(),
        add_blockchain_genesis_state=add_blockchain_genesis_state,
        validate=False,
        treasury_account_key_pair=treasury_account_key_pair
    )


def make_large_blockchain(blockchain, treasury_account_key_pair, blocks_count=100):
    accounts = blockchain.get_first_blockchain_state().account_states
    account_state = accounts[treasury_account_key_pair.public]
    assert account_state.balance > 10000000000  # tons of money present

    add_blocks(blockchain, blocks_count, treasury_account_key_pair.private)


@factory(CoinTransferTransaction)
class CoinTransferTransactionFactory(Factory):
    recipient = DEFAULT_ACCOUNT
    amount = 100
    is_fee = None
    memo = None


@factory(CoinTransferSignedChangeRequestMessage)
class CoinTransferSignedChangeRequestMessageFactory(Factory):
    balance_lock = DEFAULT_ACCOUNT
    txs = [CoinTransferTransactionFactory(amount=99), CoinTransferTransactionFactory(amount=1, is_fee=True)]


@factory(CoinTransferSignedChangeRequest)
class CoinTransferSignedChangeRequestFactory(Factory):
    signer = DEFAULT_ACCOUNT
    message = CoinTransferSignedChangeRequestMessageFactory()
    signature = None


@factory(AccountState)
class AccountStateFactory(Factory):
    balance = 1000


@factory(BlockMessage)
class CoinTransferBlockMessageFactory(Factory):
    signed_change_request = CoinTransferSignedChangeRequestFactory()
    timestamp = datetime(2021, 1, 1)
    block_type = 'ct'
    block_number = 0
    block_identifier = 'd606af9d1d769192813d71051148ef1896e3d85062c31ad3e62331e25d9c96bc'
    updated_account_states = {DEFAULT_ACCOUNT: AccountStateFactory()}


@factory(Block)
class CoinTransferBlockFactory(Factory):
    signer = DEFAULT_ACCOUNT
    message = CoinTransferBlockMessageFactory()
    hash = None  # noqa: A003
    signature = None


@factory(BlockchainStateMessage)
class InitialBlockchainStateMessageFactory(Factory):
    account_states = {DEFAULT_ACCOUNT: AccountStateFactory()}
    last_block_number = None
    last_block_identifier = None
    last_block_timestamp = None
    next_block_identifier = None


@factory(BlockchainState)
class InitialBlockchainStateFactory(Factory):
    message = InitialBlockchainStateMessageFactory()
    signer = PV_ACCOUNT


@factory(BlockchainStateMessage)
class BlockchainStateMessageFactory(Factory):
    account_states = InitialBlockchainStateMessageFactory().account_states
    last_block_number = 0
    last_block_identifier = 'd606af9d1d769192813d71051148ef1896e3d85062c31ad3e62331e25d9c96bc'
    last_block_timestamp = datetime(2021, 1, 1)
    next_block_identifier = 'c5082e9985991b717c21acf5a94a4715e1a88c3d72d478deb3d764f186d59967'


@factory(BlockchainState)
class BlockchainStateFactory(Factory):
    message = BlockchainStateMessageFactory()
    signer = PV_ACCOUNT
