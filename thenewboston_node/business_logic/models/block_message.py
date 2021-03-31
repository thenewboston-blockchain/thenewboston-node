import copy
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Optional

from dataclasses_json import config, dataclass_json
from marshmallow import fields

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.core.utils.cryptography import normalize_dict
from thenewboston_node.core.utils.dataclass import fake_super_methods

from .account_balance import BlockAccountBalance
from .base import MessageMixin
from .transfer_request import TransferRequest

logger = logging.getLogger(__name__)
validation_logger = logging.getLogger(__name__ + '.validation_logger')


def calculate_updated_balances(get_balance_value: Callable[[str], Optional[int]],
                               transfer_request: TransferRequest) -> dict[str, BlockAccountBalance]:
    updated_balances: dict[str, BlockAccountBalance] = {}
    sent_amount = 0
    for transaction in transfer_request.message.txs:
        recipient = transaction.recipient
        amount = transaction.amount

        balance = updated_balances.get(recipient)
        if balance is None:
            balance = BlockAccountBalance(value=get_balance_value(recipient) or 0)
            updated_balances[recipient] = balance

        balance.value += amount
        sent_amount += amount

    sender = transfer_request.sender
    sender_balance = get_balance_value(sender)
    assert sender_balance is not None
    assert sender_balance >= sent_amount

    updated_balances[sender] = BlockAccountBalance(
        value=sender_balance - sent_amount,
        # Transfer request message hash becomes new balance lock
        lock=transfer_request.message.get_hash()
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
    updated_balances: dict[str, BlockAccountBalance]

    def override_to_dict(self):  # this one turns into to_dict()
        dict_ = self.super_to_dict()
        # TODO(dmu) LOW: Implement a better way of removing optional fields or allow them in normalized message
        dict_['transfer_request'] = self.transfer_request.to_dict()
        dict_['updated_balances'] = {key: value.to_dict() for key, value in self.updated_balances.items()}
        return dict_

    @classmethod
    def from_transfer_request(cls, blockchain, transfer_request: TransferRequest):
        if not transfer_request.sender:
            raise ValueError('Sender must be set')

        # TODO(dmu) HIGH: Move source of time to Blockchain?
        timestamp = datetime.utcnow()

        block_number = blockchain.get_next_block_number()
        block_identifier = blockchain.get_next_block_identifier()

        return BlockMessage(
            transfer_request=copy.deepcopy(transfer_request),
            timestamp=timestamp,
            block_number=block_number,
            block_identifier=block_identifier,
            updated_balances=calculate_updated_balances(blockchain.get_balance_value, transfer_request),
        )

    def get_normalized(self) -> bytes:
        return normalize_dict(self.to_dict())  # type: ignore

    def get_balance(self, account: str) -> Optional[BlockAccountBalance]:
        return (self.updated_balances or {}).get(account)

    def validate(self, blockchain):
        validation_logger.debug('Validating block message')
        self.validate_transfer_request(blockchain)
        self.validate_block_number()

        assert self.block_number is not None
        self.validate_timestamp(blockchain)
        self.validate_block_identifier(blockchain)

        self.validate_updated_balances()
        validation_logger.debug('Block message is valid')

    def validate_transfer_request(self, blockchain):
        validation_logger.debug('Validating transfer request on block message level')
        transfer_request = self.transfer_request
        if transfer_request is None:
            raise ValidationError('Block message transfer request must present')
        validation_logger.debug('Block message transfer request is present (as expected)')

        transfer_request.validate(blockchain, self.block_number)
        validation_logger.debug('Transfer request is valid on block message level')

    def validate_timestamp(self, blockchain):
        validation_logger.debug('Validating block message timestamp')
        timestamp = self.timestamp
        if timestamp is None:
            raise ValidationError('Block message timestamp must be set')
        validation_logger.debug('Block message timestamp is set (as expected)')

        if not isinstance(timestamp, datetime):
            raise ValidationError('Block message timestamp must be datetime type')
        validation_logger.debug('Block message timestamp is a datetime type')

        if timestamp.tzinfo is not None:
            raise ValidationError('Block message timestamp must be naive datetime (UTC timezone implied)')
        validation_logger.debug('Block message timestamp is a naive datetime type')

        block_number = self.block_number
        assert block_number is not None
        if block_number > 0:
            prev_block = blockchain.get_block_by_number(block_number - 1)
            assert prev_block is not None
            if timestamp <= prev_block.message.timestamp:
                raise ValidationError('Block message timestamp must be greater than from previous block')
            validation_logger.debug('Block message timestamp is greater than from previous block')

        validation_logger.debug('Block message timestamp is valid')

    def validate_block_number(self):
        validation_logger.debug('Validating block number')
        block_number = self.block_number
        if block_number is None:
            raise ValidationError('Block number must be set')
        validation_logger.debug('Block number is set (as expected)')

        if not isinstance(block_number, int):
            raise ValidationError('Block number must be integer')
        validation_logger.debug('Block number is an integer')

        if block_number < 0:
            raise ValidationError('Block number must be greater or equal to 0')
        validation_logger.debug('Block number is greater or equal to 0')
        validation_logger.debug('Block number is valid')

    def validate_block_identifier(self, blockchain):
        validation_logger.debug('Validating block identifier')
        block_identifier = self.block_identifier
        if block_identifier is None:
            raise ValidationError('Block identifier must be set')
        validation_logger.debug('Block identifier is set')

        if not isinstance(block_identifier, str):
            raise ValidationError('Block identifier must be a string')
        validation_logger.debug('Block identifier is a string')

        block_number = self.block_number
        assert block_number is not None

        if block_identifier != blockchain.get_expected_block_identifier(block_number):
            raise ValidationError('Invalid block identifier')
        validation_logger.debug('Block identifier is valid')

    def validate_updated_balances(self):
        validation_logger.debug('Validating block message updated balances')
        updated_balances = self.updated_balances
        if updated_balances is None:
            raise ValidationError('Block message must contain updated balances')
        validation_logger.debug('Block message contains updated balances')

        if len(updated_balances) < 2:
            raise ValidationError('block message updated balances must contain at least 2 balances')
        validation_logger.debug('Block message contains at least 2 updated balances')

        sender_account_balance = updated_balances.get(self.transfer_request.sender)
        if sender_account_balance is None:
            raise ValidationError('block message updated balances must contain sender account balance')
        validation_logger.debug('Block message contains sender account in updated balances')

        if not sender_account_balance.lock:
            raise ValidationError('block message updated balances must contain sender account balance lock')
        validation_logger.debug('Block message contains sender account lock in updated balances')

        for account, account_balance in updated_balances.items():
            validation_logger.debug('Validating account %s updated balance on block message level', account)
            if not isinstance(account, str):
                raise ValidationError('Block message updated balance account must be a string')
            validation_logger.debug('Block message updated balance account %s is a string', account)

            account_balance.validate()
            validation_logger.debug(
                'Updated balance account %s updated balance is valid on block message level', account
            )

        # TODO(dmu) CRITICAL: Validate balance values
        validation_logger.debug('Block message updated balances are valid')
