from dataclasses import dataclass

from dataclasses_json import dataclass_json

from thenewboston_node.core.utils.dataclass import fake_super_methods

from ..mixins.message import MessageMixin
from ..mixins.misc import HumanizedClassNameMixin


@fake_super_methods
@dataclass_json
@dataclass
class SignedRequestMessage(MessageMixin, HumanizedClassNameMixin):
    pass
