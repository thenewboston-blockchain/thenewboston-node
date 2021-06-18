import logging
import warnings
from dataclasses import dataclass
from typing import Optional, Type, TypeVar

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models.node import PrimaryValidator, RegularNode
from thenewboston_node.business_logic.network.base import NetworkBase
from thenewboston_node.business_logic.node import get_node_signing_key
from thenewboston_node.core.logging import timeit_method, validates
from thenewboston_node.core.utils.cryptography import derive_verify_key
from thenewboston_node.core.utils.types import hexstr

from .base import BaseDataclass, get_request_to_block_type_map
from .block_message import BlockMessage
from .mixins.compactable import MessagpackCompactableMixin
from .mixins.signable import SignableMixin
from .signed_change_request import CoinTransferSignedChangeRequest, SignedChangeRequest

T = TypeVar('T', bound='Block')

logger = logging.getLogger(__name__)


@dataclass
class Block(SignableMixin, MessagpackCompactableMixin, BaseDataclass):
    """
    Blocks represent a description of change to the network.
    """
    message: BlockMessage
    message_hash: Optional[hexstr] = None

    @classmethod
    def deserialize_from_dict(cls, dict_, complain_excessive_keys=True, exclude=()):
        dict_ = dict_.copy()
        message_dict = dict_.pop('message', None)
        if message_dict is None:
            raise ValidationError('Missing keys: message')
        elif not isinstance(message_dict, dict):
            raise ValidationError('message must be a dict')

        instance_block_type = message_dict.get('block_type')
        for signed_change_request_class, (block_type, _) in get_request_to_block_type_map().items():
            if block_type == instance_block_type:
                signed_change_request_dict = message_dict.get('signed_change_request')
                if signed_change_request_dict is None:
                    raise ValidationError('Missing keys: signed_change_request')
                elif not isinstance(signed_change_request_dict, dict):
                    raise ValidationError('signed_change_request must be a dict')

                signed_change_request_obj = signed_change_request_class.deserialize_from_dict(
                    signed_change_request_dict
                )
                break
        else:
            raise NotImplementedError(f'message.block_type "{instance_block_type}" is not supported')

        message_obj = BlockMessage.deserialize_from_dict(
            message_dict, override={'signed_change_request': signed_change_request_obj}
        )

        return super().deserialize_from_dict(
            dict_, complain_excessive_keys=complain_excessive_keys, override={'message': message_obj}
        )

    @classmethod
    @timeit_method(level=logging.INFO, is_class_method=True)
    def create_from_signed_change_request(
        cls: Type[T],
        blockchain,
        signed_change_request: SignedChangeRequest,
        signing_key=None,
    ) -> T:
        signing_key = signing_key or get_node_signing_key()
        block = cls(
            signer=derive_verify_key(signing_key),
            message=BlockMessage.from_signed_change_request(blockchain, signed_change_request)
        )
        block.sign(signing_key)
        block.hash_message()
        return block

    @classmethod
    def create_from_main_transaction(
        cls: Type[T],
        blockchain,
        recipient: str,
        amount: int,
        signing_key: str,
        primary_validator: Optional[PrimaryValidator] = None,
        node: Optional[RegularNode] = None
    ) -> T:
        # TODO(dmu) HIGH: This method is only used in tests (mostly for test data creation). Business rules
        #                 do not suggest creation from main transaction. There this method must be removed
        #                 from Block interface
        if primary_validator is None or node is None:
            warnings.warn('Skipping primary_validator and node is deprecated', DeprecationWarning)
            network = NetworkBase.get_instance()
            primary_validator = primary_validator or network.get_primary_validator()
            node = node or network.get_preferred_node()

        signed_change_request = CoinTransferSignedChangeRequest.from_main_transaction(
            blockchain=blockchain,
            recipient=recipient,
            amount=amount,
            signing_key=signing_key,
            primary_validator=primary_validator,
            node=node,
        )
        return cls.create_from_signed_change_request(blockchain, signed_change_request)

    def hash_message(self) -> None:
        message_hash = self.message.get_hash()
        stored_message_hash = self.message_hash
        if stored_message_hash and stored_message_hash != message_hash:
            logger.warning('Overwriting existing message hash')

        self.message_hash = message_hash

    @validates('block')
    def validate(self, blockchain):
        with validates(f'block number {self.message.block_number} (identifier: {self.message.block_identifier})'):
            self.validate_message(blockchain)
            self.validate_message_hash()
            with validates('block signature'):
                self.validate_signature()

    @validates('block message on block level')
    def validate_message(self, blockchain):
        if not self.message:
            raise ValidationError('Block message must be not empty')

        self.message.validate(blockchain)

    @validates('block message hash')
    def validate_message_hash(self):
        if self.message.get_hash() != self.message_hash:
            raise ValidationError('Block message hash is invalid')
