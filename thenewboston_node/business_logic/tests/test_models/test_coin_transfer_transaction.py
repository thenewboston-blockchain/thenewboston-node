# coding: utf-8
import pytest

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.tests import factories


def test_validation(sample_coin_transfer_transaction):
    sample_coin_transfer_transaction.validate()


def test_recipient_validation(sample_coin_transfer_transaction):
    sample_coin_transfer_transaction.recipient = ''
    with pytest.raises(ValidationError, match='Coin transfer transaction recipient is not set'):
        sample_coin_transfer_transaction.validate()

    sample_coin_transfer_transaction.recipient = None
    with pytest.raises(ValidationError, match='Coin transfer transaction recipient is not set'):
        sample_coin_transfer_transaction.validate()


def test_amount_validation(sample_coin_transfer_transaction):
    sample_coin_transfer_transaction.amount = 1.2
    with pytest.raises(ValidationError, match='Coin transfer transaction amount must be an integer'):
        sample_coin_transfer_transaction.validate()

    sample_coin_transfer_transaction.amount = 0
    with pytest.raises(ValidationError, match='Coin transfer transaction amount must be greater or equal to 1'):
        sample_coin_transfer_transaction.validate()

    sample_coin_transfer_transaction.amount = -1
    with pytest.raises(ValidationError, match='Coin transfer transaction amount must be greater or equal to 1'):
        sample_coin_transfer_transaction.validate()


def test_fee_validation(sample_coin_transfer_transaction):
    sample_coin_transfer_transaction.fee = 'NODE'
    with pytest.raises(ValidationError, match='Coin transfer transaction fee value is invalid'):
        sample_coin_transfer_transaction.validate()


def test_validate_memo_max_length():
    memo = 'A' * 65
    transaction = factories.CoinTransferTransactionFactory(memo=memo)
    with pytest.raises(ValidationError) as exc_info:
        transaction.validate()

    assert exc_info.value.args[0] == 'Coin transfer transaction memo must be less than 64 characters'
