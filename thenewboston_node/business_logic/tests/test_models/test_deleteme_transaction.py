# coding: utf-8
import pytest

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.tests import factories


def test_validate_memo_max_length():
    memo = 'A' * 65
    transaction = factories.DeleteMeTransactionFactory(memo=memo)
    with pytest.raises(ValidationError) as exc_info:
        transaction.validate()

    assert exc_info.value.args[0] == 'Transaction memo must be less than 64 characters'


@pytest.mark.parametrize('key,value', (
    ('memo', None),
    ('fee', None),
    ('fee', False),
))
def test_transaction_optional_keys_are_not_serialized(key, value):
    transaction = factories.DeleteMeTransactionFactory(**{key: value})
    trm = factories.TransferRequestMessageFactory(txs=[transaction])
    tr = factories.TransferRequestFactory(message=trm)
    block_message = factories.BlockMessageFactory(transfer_request=tr)
    block = factories.BlockFactory(message=block_message)

    compact_dict = block.to_compact_dict(compact_values=False, compact_keys=False)

    transaction_dict = compact_dict['message']['transfer_request']['message']['txs'][0]
    assert key not in transaction_dict


def test_non_ascii_memo_is_serialized_correctly():
    memo = 'Тестовое сообщение'  # Test message in Russian
    transaction = factories.DeleteMeTransactionFactory(memo=memo)
    trm = factories.TransferRequestMessageFactory(txs=[transaction])
    tr = factories.TransferRequestFactory(message=trm)
    block_message = factories.BlockMessageFactory(transfer_request=tr)
    block = factories.BlockFactory(message=block_message)

    msg_pack = block.to_messagepack()
    restored_block = block.from_messagepack(msg_pack)

    assert restored_block == block


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
