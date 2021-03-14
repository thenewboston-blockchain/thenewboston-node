import copy
import logging
from dataclasses import dataclass, field
from datetime import datetime
from operator import itemgetter
from typing import Optional

from dataclasses_json import config, dataclass_json
from marshmallow import fields

from thenewboston_node.core.utils.cryptography import normalize_dict
from thenewboston_node.core.utils.dataclass import fake_super_methods

from .account_balance import AccountBalance
from .base import MessageMixin
from .transfer_request import TransferRequest

logger = logging.getLogger(__name__)


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
    updated_balances: list[AccountBalance]

    def override_to_dict(self):  # this one turns into to_dict()
        dict_ = self.super_to_dict()
        # TODO(dmu) LOW: Implement a better way of removing optional fields or allow them in normalized message
        dict_['transfer_request'] = self.transfer_request.to_dict()
        dict_['updated_balances'] = [balance.to_dict() for balance in self.updated_balances]
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

        updated_balances = []
        total_amount = 0
        for transaction in transfer_request.message.txs:
            recipient = transaction.recipient
            amount = transaction.amount

            balance = blockchain.get_account_balance(recipient) or 0
            updated_balances.append(AccountBalance(account=transaction.recipient, balance=balance + amount))
            total_amount += amount

        updated_balances.append(
            AccountBalance(
                account=transfer_request.sender,
                balance=total_amount,
                # Transfer request message hash becomes new balance lock
                balance_lock=transfer_request.message.get_hash()
            )
        )

        return BlockMessage(
            transfer_request=copy.deepcopy(transfer_request),
            timestamp=timestamp,
            block_number=block_number,
            block_identifier=block_identifier,
            updated_balances=updated_balances,
        )

    def get_normalized(self) -> bytes:
        message_dict = self.to_dict()  # type: ignore
        message_dict['updated_balances'] = sorted(message_dict['updated_balances'], key=itemgetter('account'))
        return normalize_dict(message_dict)

    def get_balance(self, account: str) -> Optional[AccountBalance]:
        for balance in self.updated_balances:
            if balance.account == account:
                return balance

        return None
