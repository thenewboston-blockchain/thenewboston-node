import pytest

from thenewboston_node.business_logic.tests import factories


@pytest.mark.parametrize('key,value', (
    ('memo', None),
    ('fee', None),
    ('fee', False),
))
def test_transaction_optional_keys_are_not_serialized(key, value):
    # TODO(dmu) HIGH: This test must test transaction without using outer structures
    transaction = factories.CoinTransferTransactionFactory(**{key: value})
    trm = factories.CoinTransferSignedChangeRequestMessageFactory(txs=[transaction])
    tr = factories.CoinTransferSignedChangeRequestFactory(message=trm)
    block_message = factories.BlockMessageFactory(transfer_request=tr)
    block = factories.BlockFactory(message=block_message)

    compact_dict = block.to_compact_dict(compact_values=False, compact_keys=False)

    transaction_dict = compact_dict['message']['transfer_request']['message']['txs'][0]
    assert key not in transaction_dict


def test_non_ascii_memo_is_serialized_correctly():
    # TODO(dmu) HIGH: This test must test transaction without using outer structures
    memo = 'Тестовое сообщение'  # Test message in Russian
    transaction = factories.CoinTransferTransactionFactory(memo=memo)
    trm = factories.CoinTransferSignedChangeRequestMessageFactory(txs=[transaction])
    tr = factories.CoinTransferSignedChangeRequestFactory(message=trm)
    block_message = factories.BlockMessageFactory(transfer_request=tr)
    block = factories.BlockFactory(message=block_message)

    msg_pack = block.to_messagepack()
    restored_block = block.from_messagepack(msg_pack)

    assert restored_block == block
