import pytest

from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.business_logic.tests import factories


@pytest.mark.parametrize(
    'long_name,short_name', (
        ('node_identifier', 'ni'),
        ('message', 'm'),
        ('message_hash', 'mh'),
        ('message_signature', 'ms'),
    )
)
def test_block_fields_are_compacted(long_name, short_name):
    block = factories.BlockFactory()

    block_dict = block.to_compact_dict()

    assert short_name in block_dict
    assert long_name not in block_dict


@pytest.mark.parametrize(
    'long_name,short_name', (
        ('transfer_request', 'tr'),
        ('timestamp', 't'),
        ('block_number', 'bn'),
        ('block_identifier', 'bi'),
        ('updated_balances', 'ub'),
    )
)
def test_block_message_fields_are_compacted(long_name, short_name):
    block = factories.BlockFactory()

    block_message_dict = block.to_compact_dict()['m']

    assert short_name in block_message_dict
    assert long_name not in block_message_dict


@pytest.mark.parametrize('long_name,short_name', (
    ('value', 'v'),
    ('lock', 'l'),
))
def test_updated_balances_fields_are_compacted(long_name, short_name):
    balance = factories.BlockAccountBalanceFactory(value=1000, lock='lock value')
    block_message = factories.BlockMessageFactory(updated_balances={'key': balance})
    block = factories.BlockFactory(message=block_message)

    block_balance_dict = block.to_compact_dict()['m']['ub']['key']

    assert short_name in block_balance_dict
    assert long_name not in block_balance_dict


@pytest.mark.parametrize('long_name,short_name', (
    ('sender', 's'),
    ('message', 'm'),
    ('message_signature', 'ms'),
))
def test_transfer_request_fields_are_compacted(long_name, short_name):
    block = factories.BlockFactory()

    transfer_request_dict = block.to_compact_dict()['m']['tr']

    assert short_name in transfer_request_dict
    assert long_name not in transfer_request_dict


@pytest.mark.parametrize('long_name,short_name', (('balance_lock', 'bl'),))
def test_transfer_request_message_fields_are_compacted(long_name, short_name):
    block = factories.BlockFactory()

    transfer_request_msg_dict = block.to_compact_dict()['m']['tr']['m']

    assert short_name in transfer_request_msg_dict
    assert long_name not in transfer_request_msg_dict


@pytest.mark.parametrize('long_name,short_name', (
    ('recipient', 'r'),
    ('amount', 'at'),
    ('fee', 'f'),
))
def test_transaction_fields_are_compacted(long_name, short_name):
    transaction = factories.TransactionFactory(fee=True)
    transfer_request_msg = factories.TransferRequestMessageFactory(txs=[transaction])
    transfer_request = factories.TransferRequestFactory(message=transfer_request_msg)
    message = factories.BlockMessageFactory(transfer_request=transfer_request)
    block = factories.BlockFactory(message=message)

    transaction_dict = block.to_compact_dict()['m']['tr']['m']['txs'][0]

    assert short_name in transaction_dict
    assert long_name not in transaction_dict


def test_can_load_block_from_compacted_dict():
    block = factories.BlockFactory()

    compacted = block.to_compact_dict()
    loaded_block = Block.from_compact_dict(compacted)

    assert loaded_block == block
