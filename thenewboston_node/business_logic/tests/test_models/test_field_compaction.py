import pytest

from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.business_logic.models.blockchain_state import BlockchainState
from thenewboston_node.business_logic.tests import baker_factories, factories


def test_can_load_block_from_compacted_dict():
    block = baker_factories.make_coin_transfer_block(meta=None)

    compacted = block.to_compact_dict()
    loaded_block = Block.from_compact_dict(compacted)

    assert loaded_block == block


def test_can_load_account_root_file_from_compacted_dict():
    account_root_file = factories.BlockchainStateFactory()

    compacted = account_root_file.to_compact_dict()
    loaded_account_root_file = BlockchainState.from_compact_dict(compacted)

    assert loaded_account_root_file == account_root_file


@pytest.mark.parametrize(
    'field_name,value', [
        ('signer', '4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732'),
        ('hash', '9677f4cbd7aaf32ba9615416f7bd0991b7de1434a7fa2c31add25c3355ef3959'),
        (
            'signature', (
                'd1c49087103b631a58228bdf8fb70d4789259cf22d815e207660cfe8d478adad9c'
                '7affe587942203e08be1dc1e14c6dd5a8abd8640f328e45f667a91a7c06a06'
            )
        ),
    ]
)
def test_block_fields_are_stored_in_bytes(field_name, value):
    block = factories.CoinTransferBlockFactory(**{field_name: value})

    compact_dict = block.to_compact_dict(compact_keys=False)

    assert compact_dict[field_name] == bytes.fromhex(value)


@pytest.mark.parametrize(
    'field_name,value', [('block_identifier', 'd606af9d1d769192813d71051148ef1896e3d85062c31ad3e62331e25d9c96bc')]
)
def test_block_message_fields_are_stored_in_bytes(field_name, value):
    block_msg = factories.CoinTransferBlockMessageFactory(**{field_name: value})
    block = factories.CoinTransferBlockFactory(message=block_msg)

    compact_dict = block.to_compact_dict(compact_keys=False)['message']

    assert compact_dict[field_name] == bytes.fromhex(value)


@pytest.mark.parametrize(
    'field_name,value', [
        (
            'signature', (
                'd1c49087103b631a58228bdf8fb70d4789259cf22d815e207660cfe8d478adad9c'
                '7affe587942203e08be1dc1e14c6dd5a8abd8640f328e45f667a91a7c06a06'
            )
        ),
        ('signer', 'cb0467e380e032881e3f5c26878da3584f1dc1f2262ef77ba5e1fa7ef4b2821c'),
    ]
)
def test_signed_change_request_fields_are_stored_in_bytes(field_name, value):
    signed_change_request = factories.CoinTransferSignedChangeRequestFactory(**{field_name: value})
    block_msg = factories.CoinTransferBlockMessageFactory(signed_change_request=signed_change_request)
    block = factories.CoinTransferBlockFactory(message=block_msg)

    compact_dict = block.to_compact_dict(compact_keys=False)['message']['signed_change_request']

    assert compact_dict[field_name] == bytes.fromhex(value)


@pytest.mark.parametrize(
    'field_name,value', [('balance_lock', 'cb0467e380e032881e3f5c26878da3584f1dc1f2262ef77ba5e1fa7ef4b2821c')]
)
def test_coin_transfer_signed_request_message_fields_are_stored_in_bytes(field_name, value):
    signed_change_request_msg = factories.CoinTransferSignedChangeRequestMessageFactory(**{field_name: value})
    signed_change_request = factories.CoinTransferSignedChangeRequestFactory(message=signed_change_request_msg)
    block_msg = factories.CoinTransferBlockMessageFactory(signed_change_request=signed_change_request)
    block = factories.CoinTransferBlockFactory(message=block_msg)

    compact_dict = block.to_compact_dict(compact_keys=False)['message']['signed_change_request']['message']

    assert compact_dict[field_name] == bytes.fromhex(value)


@pytest.mark.parametrize(
    'field_name,value', [('recipient', '8d3bf5323afa7a8c6bc9418288e96491a0434a98925bf392835bfdb5a4f817ff')]
)
def test_transaction_fields_are_stored_in_bytes(field_name, value):
    tx = factories.CoinTransferTransactionFactory(**{field_name: value})
    signed_change_request_msg = factories.CoinTransferSignedChangeRequestMessageFactory(txs=[tx])
    signed_change_request = factories.CoinTransferSignedChangeRequestFactory(message=signed_change_request_msg)
    block_msg = factories.CoinTransferBlockMessageFactory(signed_change_request=signed_change_request)
    block = factories.CoinTransferBlockFactory(message=block_msg)

    compact_dict = block.to_compact_dict(compact_keys=False)['message']['signed_change_request']['message']['txs'][0]

    assert compact_dict[field_name] == bytes.fromhex(value)


@pytest.mark.parametrize(
    'field_name,value', [('balance_lock', '9e310e76f63b83abef5674d5cd1445535c9aa7395a96e0381edc368a2840a598')]
)
def test_updated_balances_fields_are_stored_in_bytes(field_name, value):
    account = '1be4f03ab7ea1184dbb5e4ff53b8cf0fe1cc400150ca1476fcd10546c1b3cd6a'
    block_account_balance = factories.AccountStateFactory(**{field_name: value})
    updated_account_states = {
        account: block_account_balance,
    }
    block_msg = factories.CoinTransferBlockMessageFactory(updated_account_states=updated_account_states)
    block = factories.CoinTransferBlockFactory(message=block_msg)

    account_bytes = bytes.fromhex(account)
    compact_dict = block.to_compact_dict(compact_keys=False)['message']['updated_account_states'][account_bytes]

    assert compact_dict[field_name] == bytes.fromhex(value)


def test_updated_balances_keys_are_stored_in_bytes():
    account = '1be4f03ab7ea1184dbb5e4ff53b8cf0fe1cc400150ca1476fcd10546c1b3cd6a'
    block_account_balance = factories.AccountStateFactory()
    updated_account_states = {
        account: block_account_balance,
    }
    block_msg = factories.CoinTransferBlockMessageFactory(updated_account_states=updated_account_states)
    block = factories.CoinTransferBlockFactory(message=block_msg)

    updated_balances_dict = block.to_compact_dict(compact_keys=False)['message']['updated_account_states']

    assert set(updated_balances_dict.keys()) == {bytes.fromhex(account)}


def test_block_messagepack_with_compact_values_is_smaller():
    signature = (
        'd1c49087103b631a58228bdf8fb70d4789259cf22d815e207660cfe8d478adad9c'
        '7affe587942203e08be1dc1e14c6dd5a8abd8640f328e45f667a91a7c06a06'
    )
    message_hash = '9677f4cbd7aaf32ba9615416f7bd0991b7de1434a7fa2c31add25c3355ef3959'
    block = factories.CoinTransferBlockFactory(signature=signature, hash=message_hash)

    non_compact_size = len(block.to_messagepack(compact_keys=False, compact_values=False))
    compact_size = len(block.to_messagepack(compact_keys=False, compact_values=True))
    compaction_rate = (non_compact_size - compact_size) / non_compact_size

    assert compaction_rate > 0.3


def test_account_root_file_accounts_are_stored_in_bytes():
    account = 'cb0467e380e032881e3f5c26878da3584f1dc1f2262ef77ba5e1fa7ef4b2821c'
    account_root_file = factories.BlockchainStateFactory(account_states={account: factories.AccountStateFactory()})

    compact_dict = account_root_file.to_compact_dict(compact_keys=False)['account_states']

    assert set(compact_dict.keys()) == {bytes.fromhex(account)}
