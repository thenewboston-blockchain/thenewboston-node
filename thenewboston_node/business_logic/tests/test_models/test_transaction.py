import pytest

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.tests import factories


def test_validate_memo_max_length():
    memo = 'A' * 65
    transaction = factories.TransactionFactory(memo=memo)
    with pytest.raises(ValidationError) as exc_info:
        transaction.validate()

    assert exc_info.value.args[0] == 'Transaction memo must be less than 64 characters'


@pytest.mark.parametrize('key,value', (
    ('memo', None),
    ('fee', None),
    ('fee', False),
))
def test_transaction_optional_keys_are_not_serialized(key, value):
    transaction = factories.TransactionFactory(**{key: value})
    trm = factories.TransferRequestMessageFactory(txs=[transaction])
    tr = factories.TransferRequestFactory(message=trm)
    block_message = factories.BlockMessageFactory(transfer_request=tr)
    block = factories.BlockFactory(message=block_message)

    compact_dict = block.to_compact_dict(compact_values=False, compact_keys=False)

    transaction_dict = compact_dict['message']['transfer_request']['message']['txs'][0]
    assert key not in transaction_dict


def test_non_ascii_memo_is_serialized_correctly():
    memo = 'Тестовое сообщение'  # Test message in Russian
    transaction = factories.TransactionFactory(memo=memo)
    trm = factories.TransferRequestMessageFactory(txs=[transaction])
    tr = factories.TransferRequestFactory(message=trm)
    block_message = factories.BlockMessageFactory(transfer_request=tr)
    block = factories.BlockFactory(message=block_message)

    msg_pack = block.to_messagepack()
    restored_block = block.from_messagepack(msg_pack)

    assert restored_block == block
