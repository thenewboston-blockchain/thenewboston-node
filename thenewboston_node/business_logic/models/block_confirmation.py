from dataclasses import dataclass
from typing import Optional, Type, TypeVar

from thenewboston_node.business_logic.models import Block
from thenewboston_node.business_logic.models.base import BaseDataclass
from thenewboston_node.core.utils.cryptography import derive_public_key
from thenewboston_node.core.utils.types import hexstr

T = TypeVar('T', bound='BlockConfirmation')


# TODO(abo) HIGH: redesign to use SingableMixin, it's a temporary implementation
@dataclass
class BlockConfirmation(BaseDataclass):
    block: Block
    confirmation_signer: Optional[hexstr] = None
    confirmation_signature: Optional[hexstr] = None

    @classmethod
    def create_from_block(cls: Type[T], block: Block, cv_signing_key) -> T:
        signer = derive_public_key(cv_signing_key)
        return cls(block=block, confirmation_signer=signer)
