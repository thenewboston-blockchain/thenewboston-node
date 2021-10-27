import logging
from dataclasses import dataclass
from typing import ClassVar, Type, TypeVar

from thenewboston_node.business_logic import exceptions
from thenewboston_node.business_logic.models.constants import BlockType
from thenewboston_node.business_logic.models.node import Node
from thenewboston_node.business_logic.validators import (
    validate_exact_value, validate_greater_than_zero, validate_lte_value
)
from thenewboston_node.core.logging import timeit_method, validates
from thenewboston_node.core.utils.cryptography import derive_public_key
from thenewboston_node.core.utils.dataclass import cover_docstring, revert_docstring
from thenewboston_node.core.utils.types import hexstr

from ..account_state import AccountState
from ..signed_change_request_message import CoinTransferSignedChangeRequestMessage
from .base import SignedChangeRequest

T = TypeVar('T', bound='CoinTransferSignedChangeRequest')

logger = logging.getLogger(__name__)


@revert_docstring
@dataclass
@cover_docstring
class CoinTransferSignedChangeRequest(SignedChangeRequest):
    block_type: ClassVar[str] = BlockType.COIN_TRANSFER.value

    message: CoinTransferSignedChangeRequestMessage

    @classmethod
    @timeit_method(level=logging.INFO)
    def create_from_main_transaction(
        cls: Type[T],
        *,
        blockchain,
        recipient: hexstr,
        amount: int,
        signing_key: hexstr,
        node: Node,
        memo: str = None
    ) -> T:
        message = CoinTransferSignedChangeRequestMessage.from_main_transaction(
            blockchain=blockchain,
            coin_sender=derive_public_key(signing_key),
            recipient=recipient,
            amount=amount,
            node=node,
            memo=memo,
        )
        return cls.create_from_signed_change_request_message(message, signing_key)

    def get_sent_amount(self):
        assert self.message
        return self.message.get_total_amount()

    def get_recipient_amount(self, recipient):
        assert self.message
        return self.message.get_amount(recipient)

    @validates('coin transfer signed request')
    def validate(self, blockchain, block_number: int):
        super().validate(blockchain, block_number)
        self.validate_amount(blockchain, block_number)
        self.validate_balance_lock(blockchain, block_number)
        self.validate_circular_transactions()

    @validates('amount on transfer request level')
    def validate_amount(self, blockchain, in_block_number: int):
        balance = blockchain.get_account_balance(self.signer, in_block_number - 1)
        validate_greater_than_zero(f'{self.humanized_class_name_lowered} singer balance', balance)

        validate_lte_value(f'{self.humanized_class_name} total amount', self.message.get_total_amount(), balance)

    @validates('transfer request balance lock on transfer request level')
    def validate_balance_lock(self, blockchain, in_block_number: int):
        expected_lock = blockchain.get_account_balance_lock(self.signer, in_block_number - 1)
        validate_exact_value(
            f'{self.humanized_class_name} message balance_lock', self.message.balance_lock, expected_lock
        )

    @validates('transactions on transfer request level')
    def validate_circular_transactions(self):
        recipients = (tx.recipient for tx in self.message.txs if not tx.is_fee)
        if self.signer in recipients:
            raise exceptions.ValidationError(f'Cannot transfer coins from account {self.signer} to itself')

    @timeit_method()
    def get_updated_account_states(self, blockchain) -> dict[hexstr, AccountState]:
        last_block_number = blockchain.get_last_block_number()  # for better performance and consistency ask once

        updated_account_states: dict[hexstr, AccountState] = {}
        sent_amount = 0
        for transaction in self.message.txs:
            recipient = transaction.recipient
            amount = transaction.amount

            account_state = updated_account_states.get(recipient)
            if account_state is None:
                account_state = AccountState(balance=blockchain.get_account_balance(recipient, last_block_number))
                updated_account_states[recipient] = account_state

            assert account_state.balance is not None
            account_state.balance += amount
            sent_amount += amount
        assert sent_amount > 0

        coin_sender = self.signer
        sender_balance = blockchain.get_account_balance(coin_sender, last_block_number)
        if sent_amount > sender_balance:
            raise exceptions.CoinTransferRequestError(
                f"Sender's account {coin_sender} has not enough balance to send {sent_amount} coins"
            )

        updated_account_states[coin_sender] = AccountState(
            balance=sender_balance - sent_amount, balance_lock=self.make_balance_lock()
        )

        return updated_account_states

    def make_balance_lock(self):
        return self.message.get_hash()
