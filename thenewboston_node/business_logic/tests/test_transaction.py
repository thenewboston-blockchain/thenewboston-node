import pytest

from thenewboston_node.business_logic.exceptions import ValidationError


def test_validation(sample_transaction):
    sample_transaction.validate()


def test_recipient_validation(sample_transaction):
    sample_transaction.recipient = ''
    with pytest.raises(ValidationError, match='Transaction recipient is not set'):
        sample_transaction.validate()

    sample_transaction.recipient = None
    with pytest.raises(ValidationError, match='Transaction recipient is not set'):
        sample_transaction.validate()


def test_amount_validation(sample_transaction):
    sample_transaction.amount = 1.2
    with pytest.raises(ValidationError, match='Transaction amount must be an integer'):
        sample_transaction.validate()

    sample_transaction.amount = 0
    with pytest.raises(ValidationError, match='Transaction amount must be greater or equal to 1'):
        sample_transaction.validate()

    sample_transaction.amount = -1
    with pytest.raises(ValidationError, match='Transaction amount must be greater or equal to 1'):
        sample_transaction.validate()


def test_fee_validation(sample_transaction):
    sample_transaction.fee = 'NODE'
    with pytest.raises(ValidationError, match='Transaction fee value is invalid'):
        sample_transaction.validate()
