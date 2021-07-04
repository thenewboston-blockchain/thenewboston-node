from dataclasses import dataclass

from thenewboston_node.business_logic.models.base import BaseDataclass
from thenewboston_node.core.utils.dataclass import cover_docstring, revert_docstring

from .base import SignedChangeRequestMessage


@revert_docstring
@dataclass
@cover_docstring
class PrimaryValidatorSchedule(BaseDataclass):
    begin_block_number: int
    end_block_number: int


@revert_docstring
@dataclass
@cover_docstring
class PrimaryValidatorScheduleSignedChangeRequestMessage(SignedChangeRequestMessage):
    primary_validator_schedule: PrimaryValidatorSchedule

    def validate(self):
        # TODO(dmu) CRITICAL: Implement
        return
