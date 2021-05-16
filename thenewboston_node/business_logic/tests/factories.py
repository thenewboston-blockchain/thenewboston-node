from datetime import datetime

from thenewboston_node.business_logic.models import CoinTransferTransaction
from thenewboston_node.business_logic.models.account_balance import AccountBalance, BlockAccountBalance
from thenewboston_node.business_logic.models.account_root_file import AccountRootFile
from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.business_logic.models.block_message import BlockMessage
from thenewboston_node.business_logic.models.transfer_request import TransferRequest
from thenewboston_node.business_logic.models.transfer_request_message import TransferRequestMessage
from thenewboston_node.business_logic.utils.blockchain import generate_blockchain
from thenewboston_node.core.utils.cryptography import KeyPair, derive_verify_key
from thenewboston_node.core.utils.factory import factory

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
class CoinTransferTransactionFactory:
    recipient = DEFAULT_ACCOUNT
    amount = 100
    fee = None
    memo = None


@factory(CoinTransferTransaction)
class DeleteMeTransactionFactory:
    recipient = DEFAULT_ACCOUNT
    amount = 100
    fee = None
    memo = None


@factory(TransferRequestMessage)
class TransferRequestMessageFactory:
    balance_lock = DEFAULT_ACCOUNT
    txs = [DeleteMeTransactionFactory(amount=99), DeleteMeTransactionFactory(amount=1, fee=True)]  # type: ignore


@factory(TransferRequest)
class TransferRequestFactory:
    sender = DEFAULT_ACCOUNT
    message = TransferRequestMessageFactory()
    message_signature = None


@factory(AccountBalance)
class AccountBalanceFactory:
    value = 1000
    lock = '9e310e76f63b83abef5674d5cd1445535c9aa7395a96e0381edc368a2840a598'


@factory(BlockAccountBalance)
class BlockAccountBalanceFactory:
    value = 1000
    lock = '9e310e76f63b83abef5674d5cd1445535c9aa7395a96e0381edc368a2840a598'


@factory(BlockMessage)
class BlockMessageFactory:
    transfer_request = TransferRequestFactory()
    timestamp = datetime(2021, 1, 1)
    block_number = 1000
    block_identifier = 'd606af9d1d769192813d71051148ef1896e3d85062c31ad3e62331e25d9c96bc'
    updated_balances = {DEFAULT_ACCOUNT: BlockAccountBalanceFactory()}


@factory(Block)
class BlockFactory:
    node_identifier = DEFAULT_ACCOUNT
    message = BlockMessageFactory()
    message_hash = None
    message_signature = None


@factory(AccountRootFile)
class AccountRootFileFactory:
    accounts = {DEFAULT_ACCOUNT: AccountBalanceFactory()}
    last_block_number = None
    last_block_identifier = None
    last_block_timestamp = None
