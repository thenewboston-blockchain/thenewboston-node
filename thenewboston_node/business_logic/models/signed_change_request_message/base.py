from dataclasses import dataclass

from thenewboston_node.business_logic.models.base import BaseDataclass

from ..mixins.message import MessageMixin
from ..mixins.misc import HumanizedClassNameMixin


@dataclass
class SignedChangeRequestMessage(MessageMixin, HumanizedClassNameMixin, BaseDataclass):
    pass
