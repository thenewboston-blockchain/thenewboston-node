import copy
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Optional

from dataclasses_json import config, dataclass_json
from marshmallow import fields

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.validators import (
    validate_empty, validate_exact_value, validate_min_item_count, validate_not_empty, validate_type
)
from thenewboston_node.core.logging import validates
from thenewboston_node.core.utils.cryptography import normalize_dict
from thenewboston_node.core.utils.dataclass import fake_super_methods

from . import AccountState
from .mixins.message import MessageMixin
from .mixins.misc import HumanizedClassNameMixin
from .signed_request import CoinTransferSignedRequest

logger = logging.getLogger(__name__)


def make_balance_lock(transfer_request):
    assert transfer_request.message
    return transfer_request.message.get_hash()


def calculate_updated_balances(
    get_account_balance: Callable[[str], Optional[int]], transfer_request: CoinTransferSignedRequest
) -> dict[str, AccountState]:
    updated_account_states: dict[str, AccountState] = {}
    sent_amount = 0
    for transaction in transfer_request.message.txs:
        recipient = transaction.recipient
        amount = transaction.amount

        account_state = updated_account_states.get(recipient)
        if account_state is None:
            account_state = AccountState(balance=get_account_balance(recipient) or 0)
            updated_account_states[recipient] = account_state

        assert account_state.balance is not None
        account_state.balance += amount
        sent_amount += amount

    coin_sender = transfer_request.signer
    sender_balance = get_account_balance(coin_sender)
    assert sender_balance is not None
    assert sender_balance >= sent_amount

    updated_account_states[coin_sender] = AccountState(
        balance=sender_balance - sent_amount, balance_lock=make_balance_lock(transfer_request)
    )

    return updated_account_states


@fake_super_methods
@dataclass_json
@dataclass
class BlockMessage(MessageMixin, HumanizedClassNameMixin):
    """
    Contains requested changes in the network like transfer of coins, etc...
    """
    transfer_request: CoinTransferSignedRequest
    """Requested changes"""

    # We need timestamp, block_number and block_identifier to be signed and hashed therefore
    # they are include in BlockMessage, not in Block
    timestamp: datetime = field(  # naive datetime in UTC
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,
            mm_field=fields.DateTime(format='iso')
        )
    )
    """Block timestamp in UTC"""

    block_number: int
    """Sequential block number"""

    block_identifier: str
    """Unique block identifier"""

    updated_account_states: dict[str, AccountState]
    """Updated account states: {"account_number": `AccountState`_, ...}"""

    def override_to_dict(self):  # this one turns into to_dict()
        dict_ = self.super_to_dict()
        # TODO(dmu) LOW: Implement a better way of removing optional fields or allow them in normalized message
        dict_['transfer_request'] = self.transfer_request.to_dict()
        dict_['updated_account_states'] = {key: value.to_dict() for key, value in self.updated_account_states.items()}
        return dict_

    @classmethod
    def from_coin_transfer_signed_request(cls, blockchain, coin_transfer_signed_request: CoinTransferSignedRequest):
        if not coin_transfer_signed_request.signer:
            raise ValueError('Sender must be set')

        # TODO(dmu) HIGH: Move source of time to Blockchain?
        timestamp = datetime.utcnow()

        block_number = blockchain.get_next_block_number()
        block_identifier = blockchain.get_next_block_identifier()

        return BlockMessage(
            transfer_request=copy.deepcopy(coin_transfer_signed_request),
            timestamp=timestamp,
            block_number=block_number,
            block_identifier=block_identifier,
            updated_account_states=calculate_updated_balances(
                blockchain.get_account_balance, coin_transfer_signed_request
            ),
        )

    def get_normalized(self) -> bytes:
        return normalize_dict(self.to_dict())  # type: ignore

    def get_balance(self, account: str) -> Optional[AccountState]:
        return (self.updated_account_states or {}).get(account)

    def get_sent_amount(self):
        assert self.transfer_request
        return self.transfer_request.get_sent_amount()

    def get_recipient_amount(self, recipient):
        assert self.transfer_request
        return self.transfer_request.get_recipient_amount(recipient)

    @validates('block message')
    def validate(self, blockchain):
        self.validate_transfer_request(blockchain)
        self.validate_block_number()

        assert self.block_number is not None
        self.validate_timestamp(blockchain)
        self.validate_block_identifier(blockchain)

        self.validate_updated_account_states(blockchain)

    @validates('transfer request on block message level')
    def validate_transfer_request(self, blockchain):
        transfer_request = self.transfer_request
        if transfer_request is None:
            raise ValidationError('Block message transfer request must present')

        transfer_request.validate(blockchain, self.block_number)

    @validates('block message timestamp')
    def validate_timestamp(self, blockchain):
        timestamp = self.timestamp
        if timestamp is None:
            raise ValidationError('Block message timestamp must be set')

        if not isinstance(timestamp, datetime):
            raise ValidationError('Block message timestamp must be datetime type')

        if timestamp.tzinfo is not None:
            raise ValidationError('Block message timestamp must be naive datetime (UTC timezone implied)')

        block_number = self.block_number
        assert block_number is not None

        if block_number > 0:
            prev_block_number = block_number - 1
            prev_block = blockchain.get_block_by_number(prev_block_number)
            if prev_block is None:
                logger.debug('Partial blockchain detected')
                account_root_file = blockchain.get_closest_account_root_file(block_number)
                if account_root_file is None:
                    raise ValidationError('Unexpected could not find base account root file')

                if account_root_file.is_initial():
                    raise ValidationError('Unexpected initial account root file found')

                if account_root_file.last_block_number != prev_block_number:
                    raise ValidationError('Base account root file block number mismatch')

                assert account_root_file.last_block_timestamp
                min_timestamp = account_root_file.last_block_timestamp
            else:
                min_timestamp = prev_block.message.timestamp

            if timestamp <= min_timestamp:
                raise ValidationError('Block message timestamp must be greater than from previous block')

    @validates('block number')
    def validate_block_number(self):
        block_number = self.block_number
        if block_number is None:
            raise ValidationError('Block number must be set')

        if not isinstance(block_number, int):
            raise ValidationError('Block number must be integer')

        if block_number < 0:
            raise ValidationError('Block number must be greater or equal to 0')

    @validates('block identifier')
    def validate_block_identifier(self, blockchain):
        block_identifier = self.block_identifier
        if block_identifier is None:
            raise ValidationError('Block identifier must be set')

        if not isinstance(block_identifier, str):
            raise ValidationError('Block identifier must be a string')

        block_number = self.block_number
        assert block_number is not None

        if block_identifier != blockchain.get_expected_block_identifier(block_number):
            raise ValidationError('Invalid block identifier')

    @validates()
    def validate_updated_account_states(self, blockchain):
        updated_account_states = self.updated_account_states

        humanized_class_name = self.humanized_class_name_lowered
        validate_not_empty(f'{humanized_class_name} updated_account_states', updated_account_states)
        validate_min_item_count(f'{humanized_class_name} updated_account_states', updated_account_states, 2)

        signer = self.transfer_request.signer
        sender_account_state = self.updated_account_states.get(signer)
        validate_not_empty(f'{humanized_class_name} updated_account_states.{signer}', sender_account_state)

        for account_number, account_state in updated_account_states.items():
            with validates(f'{humanized_class_name} account {account_number} updated state'):
                account_subject = f'{humanized_class_name} updated_account_states key (account number)'
                validate_not_empty(account_subject, account_number)
                validate_type(account_subject, account_number, str)

                account_state.validate()
                is_sender = account_number == signer
                self.validate_updated_account_balance_lock(
                    account_number=account_number, account_state=account_state, is_sender=is_sender
                )
                self.validate_updated_account_balance(
                    account_number=account_number,
                    account_state=account_state,
                    blockchain=blockchain,
                    is_sender=is_sender
                )

    @validates('account {account_number} balance lock')
    def validate_updated_account_balance_lock(self, *, account_number, account_state, is_sender=False):
        subject = (
            f'{self.humanized_class_name_lowered} {"sender" if is_sender else "recipient"} account '
            f'{account_number} balance_lock'
        )
        balance_lock = account_state.balance_lock

        if is_sender:
            validate_not_empty(subject, balance_lock)
            validate_type(subject, balance_lock, str)
            validate_exact_value(subject, balance_lock, make_balance_lock(self.transfer_request))
        else:
            validate_empty(subject, balance_lock)

    @validates('account {account_number} balance value')
    def validate_updated_account_balance(self, *, account_number, account_state, blockchain, is_sender=False):
        subject = (
            f'{self.humanized_class_name_lowered} {"sender" if is_sender else "recipient"} account '
            f'{account_number}'
        )

        current_balance = blockchain.get_account_balance(account_number, self.block_number)
        if is_sender:
            validate_not_empty(f'sender account {account_number} current balance', current_balance)
            expected_balance = current_balance - self.get_sent_amount()
        else:
            expected_balance = (current_balance or 0) + self.get_recipient_amount(account_number)

        validate_exact_value(f'{subject} balance', account_state.balance, expected_balance)
