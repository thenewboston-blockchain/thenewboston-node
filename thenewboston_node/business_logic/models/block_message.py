import copy
import logging
from dataclasses import dataclass, field
from datetime import datetime
from operator import itemgetter

from dataclasses_json import config, dataclass_json
from marshmallow import fields

from thenewboston_node.core.utils.cryptography import hash_normalized_message, normalize_dict_message
from thenewboston_node.core.utils.dataclass import fake_super_methods

from .account_balance import AccountBalance
from .transfer_request import TransferRequest

logger = logging.getLogger(__name__)


@fake_super_methods
@dataclass_json
@dataclass
class BlockMessage:
    transfer_request: TransferRequest
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
        timestamp = datetime.utcnow()

        # TODO(dmu) LOW: Find a better way to avoid circular imports
        from ..blockchain import get_blockchain  # avoid circular imports
        blockchain = get_blockchain()
        head_block = blockchain.get_head_block()
        if head_block:
            block_number = head_block.message.block_number + 1
            block_identifier = head_block.message_hash
        else:
            block_number = 0
            block_identifier = blockchain.get_genesis_block_identifier()

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

    def get_hash(self):
        normalized_message = self.get_normalized()
        message_hash = hash_normalized_message(normalized_message)
        logger.debug('Got %s hash for message: %r', message_hash, normalized_message)
        return message_hash

    def get_normalized(self) -> bytes:
        message_dict = self.to_dict()  # type: ignore
        message_dict['updated_balances'] = sorted(message_dict['updated_balances'], key=itemgetter('account'))
        return normalize_dict_message(message_dict)
