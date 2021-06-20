import copy
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.validators import (
    validate_empty, validate_exact_value, validate_greater_than_zero, validate_gt_value, validate_gte_value,
    validate_is_none, validate_min_item_count, validate_not_empty, validate_not_none, validate_type
)
from thenewboston_node.core.logging import validates
from thenewboston_node.core.utils.dataclass import cover_docstring, revert_docstring
from thenewboston_node.core.utils.types import hexstr

from . import AccountState
from .base import BaseDataclass, BlockType, get_request_to_block_type_map  # noqa: I101
from .mixins.message import MessageMixin
from .signed_change_request import SignedChangeRequest

logger = logging.getLogger(__name__)


@revert_docstring
@dataclass
@cover_docstring
class BlockMessage(MessageMixin, BaseDataclass):
    block_type: str = field(metadata={'example_value': BlockType.COIN_TRANSFER.value})
    """One of the `Block types`_"""

    signed_change_request: SignedChangeRequest

    # We need timestamp, block_number and block_identifier to be signed and hashed therefore
    # they are included in BlockMessage, not in Block model
    timestamp: datetime = field(metadata={'example_value': datetime(2021, 6, 20, 12, 41, 2, 994406)})
    block_number: int = field(metadata={'example_value': 3})
    block_identifier: hexstr = field(
        metadata={'example_value': 'b0dabd367eb1ed670ab9ce4cef9d45106332f211c7b50ddd60dec4ae62711fb7'}
    )
    updated_account_states: dict[hexstr, AccountState] = field(
        metadata={'example_value': {
            '657cf373f6f8fb72854bd302269b8b2b3576e3e2a686bd7d0a112babaa1790c6': {}
        }}
    )

    @classmethod
    def deserialize_from_dict(cls, dict_, complain_excessive_keys=True, override=None):
        override = override or {}
        if 'updated_account_states' in dict_ and 'updated_account_states' not in override:
            logger.debug(
                'updated_account_states = %s is not overridden (will override)', dict['updated_account_states']
            )
            dict_ = dict_.copy()
            updated_account_states_dict = dict_.pop('updated_account_states')
            item_values_override = {
                key: {
                    'node': {
                        'identifier': key
                    }
                } for key, value in updated_account_states_dict.items()
            }
            logger.debug('item_values_override = %s', item_values_override)

            updated_account_states_obj = cls.deserialize_from_inner_dict(
                cls.get_field_type('updated_account_states'),
                updated_account_states_dict,
                complain_excessive_keys=complain_excessive_keys,
                item_values_override=item_values_override
            )

            logger.debug('updated_account_states_obj = %s', updated_account_states_obj)
            override['updated_account_states'] = updated_account_states_obj

        return super().deserialize_from_dict(dict_, complain_excessive_keys=complain_excessive_keys, override=override)

    @classmethod
    def from_signed_change_request(cls, blockchain, signed_change_request: SignedChangeRequest):
        if not signed_change_request.signer:
            raise ValueError('Sender must be set')

        for class_, (block_type, get_updated_account_states) in get_request_to_block_type_map().items():  # noqa: B007
            if isinstance(signed_change_request, class_):
                updated_account_states = get_updated_account_states(signed_change_request, blockchain)
                break
        else:
            raise NotImplementedError(f'signed_change_request type {type(signed_change_request)} is not supported')

        assert block_type

        timestamp = blockchain.utcnow()

        block_number = blockchain.get_next_block_number()
        block_identifier = blockchain.get_next_block_identifier()

        return BlockMessage(
            block_type=block_type,
            signed_change_request=copy.deepcopy(signed_change_request),
            timestamp=timestamp,
            block_number=block_number,
            block_identifier=block_identifier,
            updated_account_states=updated_account_states
        )

    def get_account_state(self, account: hexstr) -> Optional[AccountState]:
        return (self.updated_account_states or {}).get(account)

    def get_sent_amount(self):
        assert self.signed_change_request
        return self.signed_change_request.get_sent_amount()

    def get_recipient_amount(self, recipient):
        assert self.signed_change_request
        return self.signed_change_request.get_recipient_amount(recipient)

    @validates('block message')
    def validate(self, blockchain):
        self.validate_signed_change_request(blockchain)
        self.validate_block_number()

        assert self.block_number is not None
        self.validate_timestamp(blockchain)
        self.validate_block_identifier(blockchain)

        self.validate_updated_account_states(blockchain)

    @validates('transfer request on block message level')
    def validate_signed_change_request(self, blockchain):
        signed_change_request = self.signed_change_request
        validate_not_none(f'{self.humanized_class_name} signed_change_request', self.signed_change_request)
        signed_change_request.validate(blockchain, self.block_number)

    @validates('block message timestamp')
    def validate_timestamp(self, blockchain):
        timestamp = self.timestamp
        validate_not_none(f'{self.humanized_class_name} timestamp', timestamp)
        validate_type(f'{self.humanized_class_name} timestamp', timestamp, datetime)
        validate_is_none(f'{self.humanized_class_name} timestamp timezone', timestamp.tzinfo)

        block_number = self.block_number
        assert block_number is not None

        if block_number > 0:
            prev_block_number = block_number - 1
            prev_block = blockchain.get_block_by_number(prev_block_number)
            if prev_block is None:
                logger.debug('Partial blockchain detected')
                blockchain_state = blockchain.get_closest_blockchain_state_snapshot(block_number)
                validate_not_none('Closest blockchain state', blockchain_state)

                if blockchain_state.is_initial():
                    raise ValidationError('Unexpected initial account root file found')

                validate_exact_value(
                    'Blockchain state last block number', blockchain_state.last_block_number, prev_block_number
                )

                assert blockchain_state.last_block_timestamp
                min_timestamp = blockchain_state.last_block_timestamp
            else:
                min_timestamp = prev_block.message.timestamp

            validate_gt_value(f'{self.humanized_class_name} timestamp', timestamp, min_timestamp)

    @validates('block number')
    def validate_block_number(self):
        block_number = self.block_number
        validate_not_none(f'{self.humanized_class_name} block_number', block_number)
        validate_type(f'{self.humanized_class_name} block_number', block_number, int)
        validate_gte_value(f'{self.humanized_class_name} block_number', block_number, 0)

    @validates('block identifier')
    def validate_block_identifier(self, blockchain):
        block_identifier = self.block_identifier
        validate_not_none(f'{self.humanized_class_name} block_identifier', block_identifier)
        validate_type(f'{self.humanized_class_name} block_identifier', block_identifier, str)

        block_number = self.block_number
        assert block_number is not None

        expected_identifier = blockchain.get_expected_block_identifier(block_number)
        validate_exact_value(f'{self.humanized_class_name} block_identifier', block_identifier, expected_identifier)

    @validates()
    def validate_updated_account_states(self, blockchain):
        updated_account_states = self.updated_account_states

        humanized_class_name = self.humanized_class_name_lowered
        validate_not_empty(f'{humanized_class_name} updated_account_states', updated_account_states)

        from .signed_change_request import CoinTransferSignedChangeRequest
        if isinstance(self.signed_change_request, CoinTransferSignedChangeRequest):
            validate_min_item_count(f'{humanized_class_name} updated_account_states', updated_account_states, 2)

            signer = self.signed_change_request.signer
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
            from ..algorithms.updated_account_states.coin_transfer import make_balance_lock
            validate_exact_value(subject, balance_lock, make_balance_lock(self.signed_change_request))
        else:
            validate_empty(subject, balance_lock)

    @validates('account {account_number} balance value')
    def validate_updated_account_balance(self, *, account_number, account_state, blockchain, is_sender=False):
        subject = (
            f'{self.humanized_class_name_lowered} {"sender" if is_sender else "recipient"} account '
            f'{account_number}'
        )

        balance = blockchain.get_account_balance(account_number, self.block_number - 1)
        if is_sender:
            validate_greater_than_zero(f'sender account {account_number} current balance', balance)
            expected_balance = balance - self.get_sent_amount()
        else:
            expected_balance = balance + self.get_recipient_amount(account_number)

        validate_exact_value(f'{subject} balance', account_state.balance, expected_balance)
