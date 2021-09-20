import logging
from copy import deepcopy
from dataclasses import dataclass
from typing import ClassVar, Optional, Type, TypeVar

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.core.utils.dataclass import cover_docstring, revert_docstring
from thenewboston_node.core.utils.types import hexstr

from ..account_state import AccountState
from ..signed_change_request_message import PrimaryValidatorSchedule, PrimaryValidatorScheduleSignedChangeRequestMessage
from .base import SignedChangeRequest
from .constants import BlockType

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='PrimaryValidatorScheduleSignedChangeRequest')


@revert_docstring
@dataclass
@cover_docstring
class PrimaryValidatorScheduleSignedChangeRequest(SignedChangeRequest):
    block_type: ClassVar[str] = BlockType.PRIMARY_VALIDATOR_SCHEDULE.value

    message: PrimaryValidatorScheduleSignedChangeRequestMessage

    @classmethod
    def create(
        cls: Type[T],
        begin_block_number: int,
        end_block_number: int,
        signing_key: hexstr,
    ) -> T:
        message = PrimaryValidatorScheduleSignedChangeRequestMessage(
            primary_validator_schedule=PrimaryValidatorSchedule(
                begin_block_number=begin_block_number,
                end_block_number=end_block_number,
            )
        )
        return cls.create_from_signed_change_request_message(message, signing_key)

    def get_updated_account_states(self, blockchain) -> dict[hexstr, AccountState]:
        return {
            self.signer: AccountState(primary_validator_schedule=deepcopy(self.message.primary_validator_schedule))
        }

    def validate(self, blockchain, block_number: Optional[int] = None):
        super().validate(blockchain, block_number)
        self.validate_node(blockchain, block_number)

    def validate_node(self, blockchain, block_number=None):
        node = blockchain.get_node_by_identifier(
            identifier=self.signer, on_block_number=block_number - 1 if block_number else None
        )
        if node is None:
            raise ValidationError('Signer node must be declared in the blockchain before primary validator schedule')
