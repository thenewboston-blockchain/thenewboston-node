import copy
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Optional

from dataclasses_json import config, dataclass_json
from marshmallow import fields

from thenewboston_node.core.utils.cryptography import normalize_dict
from thenewboston_node.core.utils.dataclass import fake_super_methods

from .account_balance import AccountBalance
from .base import MessageMixin
from .transfer_request import TransferRequest

logger = logging.getLogger(__name__)


def calculate_updated_balances(get_account_balance: Callable[[str], Optional[int]],
                               transfer_request: TransferRequest) -> dict[str, AccountBalance]:
    updated_balances: dict[str, AccountBalance] = {}
    sent_amount = 0
    for transaction in transfer_request.message.txs:
        recipient = transaction.recipient
        amount = transaction.amount

        balance = updated_balances.get(recipient)
        if balance is None:
            balance = AccountBalance(balance=get_account_balance(recipient) or 0)
            updated_balances[recipient] = balance

        balance.balance += amount
        sent_amount += amount

    sender = transfer_request.sender
    sender_balance = get_account_balance(sender)
    assert sender_balance is not None
    assert sender_balance >= sent_amount

    updated_balances[sender] = AccountBalance(
        balance=sender_balance - sent_amount,
        # Transfer request message hash becomes new balance lock
        balance_lock=transfer_request.message.get_hash()
    )

    return updated_balances


@fake_super_methods
@dataclass_json
@dataclass
class BlockMessage(MessageMixin):
    transfer_request: TransferRequest
    # We need timestamp, block_number and block_identifier to be signed and hashed therefore
    # they are include in BlockMessage, not in Block
    timestamp: datetime = field(  # naive datetime in UTC
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,
            mm_field=fields.DateTime(format='iso')
        )
    )
    block_number: int
    block_identifier: str
    updated_balances: dict[str, AccountBalance]

    def override_to_dict(self):  # this one turns into to_dict()
        dict_ = self.super_to_dict()
        # TODO(dmu) LOW: Implement a better way of removing optional fields or allow them in normalized message
        dict_['transfer_request'] = self.transfer_request.to_dict()
        dict_['updated_balances'] = {key: value.to_dict() for key, value in self.updated_balances.items()}
        return dict_

    @classmethod
    def from_transfer_request(cls, transfer_request: TransferRequest):
        if not transfer_request.sender:
            raise ValueError('Sender must be set')

        timestamp = datetime.utcnow()

        # TODO(dmu) LOW: Find a better way to avoid circular imports
        from ..blockchain.base import BlockchainBase  # avoid circular imports
        blockchain = BlockchainBase.get_instance()
        head_block = blockchain.get_head_block()
        if head_block:
            block_number = head_block.message.block_number + 1
            # Previous Block message hash becomes block identifier
            block_identifier = head_block.message_hash
        else:
            block_number = 0
            block_identifier = blockchain.get_genesis_block_identifier()

        assert block_identifier

        return BlockMessage(
            transfer_request=copy.deepcopy(transfer_request),
            timestamp=timestamp,
            block_number=block_number,
            block_identifier=block_identifier,
            updated_balances=calculate_updated_balances(blockchain.get_account_balance, transfer_request),
        )

    def get_normalized(self) -> bytes:
        return normalize_dict(self.to_dict())  # type: ignore

    def get_balance(self, account: str) -> Optional[AccountBalance]:
        return (self.updated_balances or {}).get(account)
