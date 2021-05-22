from dataclasses import dataclass
from typing import TypeVar

from dataclasses_json import dataclass_json

from thenewboston_node.core.utils.dataclass import fake_super_methods

from ..base import HumanizedClassNameMixin, MessageMixin

T = TypeVar('T', bound='SignedRequestMessage')


@fake_super_methods
@dataclass_json
@dataclass
class SignedRequestMessage(MessageMixin, HumanizedClassNameMixin):
    pass
