from datetime import datetime

from thenewboston_node.business_logic.models.account_balance import AccountBalance, BlockAccountBalance
from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.business_logic.models.block_message import BlockMessage
from thenewboston_node.business_logic.models.transaction import Transaction
from thenewboston_node.business_logic.models.transfer_request import TransferRequest
from thenewboston_node.business_logic.models.transfer_request_message import TransferRequestMessage
from thenewboston_node.core.utils.factory import factory

DEFAULT_ACCOUNT = 'd5356888dc9303e44ce52b1e06c3165a7759b9df1e6a6dfbd33ee1c3df1ab4d1'


@factory(Transaction)
class TransactionFactory:
    recipient = DEFAULT_ACCOUNT
    amount = 100
    fee = None


@factory(TransferRequestMessage)
class TransferRequestMessageFactory:
    balance_lock = DEFAULT_ACCOUNT
    txs = [TransactionFactory(amount=99), TransactionFactory(amount=1, fee=True)]  # type: ignore


@factory(TransferRequest)
class TransferRequestFactory:
    sender = DEFAULT_ACCOUNT
    message = TransferRequestMessageFactory()
    message_signature = None


@factory(AccountBalance)
class AccountBalanceFactory:
    value = 1000
    lock = 'test value'


@factory(BlockAccountBalance)
class BlockAccountBalanceFactory:
    value = 1000
    lock = 'test value'


@factory(BlockMessage)
class BlockMessageFactory:
    transfer_request = TransferRequestFactory()
    timestamp = datetime(2021, 1, 1)
    block_number = 1000
    block_identifier = 2000
    updated_balances = {'test key': BlockAccountBalanceFactory()}


@factory(Block)
class BlockFactory:
    node_identifier = DEFAULT_ACCOUNT
    message = BlockMessageFactory()
    message_hash = None
    message_signature = None
