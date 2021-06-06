from dataclasses import dataclass

from thenewboston_node.business_logic.models.base import BaseDataclass

from ..mixins.message import MessageMixin


@dataclass
class SignedChangeRequestMessage(MessageMixin, BaseDataclass):
    pass
