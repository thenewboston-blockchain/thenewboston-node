from dataclasses import dataclass

from thenewboston_node.business_logic.models.base import BaseDataclass
from thenewboston_node.core.utils.dataclass import cover_docstring, revert_docstring

from ..mixins.message import MessageMixin


@revert_docstring
@dataclass
@cover_docstring
class SignedChangeRequestMessage(MessageMixin, BaseDataclass):
    pass
