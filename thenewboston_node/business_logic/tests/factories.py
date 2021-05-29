from datetime import datetime

from thenewboston_node.business_logic.models import (
    CoinTransferSignedRequest, CoinTransferSignedRequestMessage, CoinTransferTransaction
)
from thenewboston_node.business_logic.models.account_balance import AccountState, BlockAccountBalance
from thenewboston_node.business_logic.models.account_root_file import AccountRootFile
from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.business_logic.models.block_message import BlockMessage
from thenewboston_node.business_logic.utils.blockchain import generate_blockchain
from thenewboston_node.core.utils.cryptography import KeyPair, derive_verify_key
from thenewboston_node.core.utils.factory import Factory, factory

DEFAULT_ACCOUNT = 'd5356888dc9303e44ce52b1e06c3165a7759b9df1e6a6dfbd33ee1c3df1ab4d1'


def add_blocks_to_blockchain(blockchain, block_count, treasury_account_private_key):
    treasury_account_key_pair = KeyPair(
        public=derive_verify_key(treasury_account_private_key), private=treasury_account_private_key
    )
    generate_blockchain(
        blockchain,
        block_count,
        add_initial_account_root_file=False,
        validate=False,
        treasury_account_key_pair=treasury_account_key_pair
    )


@factory(CoinTransferTransaction)
class CoinTransferTransactionFactory(Factory):
    recipient = DEFAULT_ACCOUNT
    amount = 100
    fee = None
    memo = None


@factory(CoinTransferSignedRequestMessage)
class CoinTransferSignedRequestMessageFactory(Factory):
    balance_lock = DEFAULT_ACCOUNT
    txs = [CoinTransferTransactionFactory(amount=99), CoinTransferTransactionFactory(amount=1, fee=True)]


@factory(CoinTransferSignedRequest)
class CoinTransferSignedRequestFactory(Factory):
    signer = DEFAULT_ACCOUNT
    message = CoinTransferSignedRequestMessageFactory()
    signature = None


@factory(AccountState)
class AccountBalanceFactory(Factory):
    balance = 1000
    balance_lock = DEFAULT_ACCOUNT


@factory(BlockAccountBalance)
class BlockAccountBalanceFactory(Factory):
    balance = 1000
    balance_lock = DEFAULT_ACCOUNT


@factory(BlockMessage)
class BlockMessageFactory(Factory):
    transfer_request = CoinTransferSignedRequestFactory()
    timestamp = datetime(2021, 1, 1)
    block_number = 0
    block_identifier = 'd606af9d1d769192813d71051148ef1896e3d85062c31ad3e62331e25d9c96bc'
    updated_balances = {DEFAULT_ACCOUNT: BlockAccountBalanceFactory()}


@factory(Block)
class BlockFactory(Factory):
    signer = DEFAULT_ACCOUNT
    message = BlockMessageFactory()
    message_hash = None
    signature = None


@factory(AccountRootFile)
class InitialAccountRootFileFactory(Factory):
    accounts = {DEFAULT_ACCOUNT: AccountBalanceFactory()}
    last_block_number = None
    last_block_identifier = None
    last_block_timestamp = None
    next_block_identifier = None


@factory(AccountRootFile)
class AccountRootFileFactory(Factory):
    accounts = {DEFAULT_ACCOUNT: AccountBalanceFactory()}
    last_block_number = 0
    last_block_identifier = 'd606af9d1d769192813d71051148ef1896e3d85062c31ad3e62331e25d9c96bc'
    last_block_timestamp = datetime(2021, 1, 1)
    next_block_identifier = 'c5082e9985991b717c21acf5a94a4715e1a88c3d72d478deb3d764f186d59967'
