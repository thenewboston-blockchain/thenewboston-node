from datetime import datetime, timedelta

import pytest

from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.business_logic.node import get_signing_key
from thenewboston_node.core.utils.cryptography import derive_verify_key


@pytest.mark.usefixtures(
    'forced_mock_blockchain', 'get_head_block_mock', 'get_initial_account_root_file_hash_mock',
    'get_account_balance_mock'
)
def test_can_create_block_from_transfer_request(sample_transfer_request):
    block = Block.from_transfer_request(sample_transfer_request)
    assert block.message
    assert block.message_hash
    assert block.message_signature
    assert block.is_signature_valid()
    assert block.node_identifier
    assert block.node_identifier == derive_verify_key(get_signing_key())

    block_message = block.message

    transfer_request = block_message.transfer_request
    assert transfer_request == sample_transfer_request
    assert transfer_request is not sample_transfer_request  # test that a copy of it was made

    assert isinstance(block_message.timestamp, datetime)
    assert block_message.timestamp.tzinfo is None
    assert block_message.timestamp - datetime.utcnow() < timedelta(seconds=1)

    assert block_message.block_number == 0
    assert block_message.block_identifier == 'fake-block-identifier'
    assert isinstance(block_message.updated_balances, list)
    assert len(block_message.updated_balances) == 4
    assert all(balance.account for balance in block_message.updated_balances)
    assert all(balance.balance for balance in block_message.updated_balances)


@pytest.mark.usefixtures(
    'forced_mock_blockchain', 'get_head_block_mock', 'get_initial_account_root_file_hash_mock',
    'get_account_balance_mock'
)
def test_normalized_block_message(sample_transfer_request):
    expected_message_template = (
        '{"block_identifier":"fake-block-identifier","block_number":0,"timestamp":"<replace-with-timestamp>",'
        '"transfer_request":{"message":{"balance_lock":'
        '"4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732","txs":'
        '[{"amount":425,"recipient":"484b3176c63d5f37d808404af1a12c4b9649cd6f6769f35bdf5a816133623fbc"},'
        '{"amount":1,"fee":"NODE","recipient":"5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8"},'
        '{"amount":4,"fee":"PRIMARY_VALIDATOR","recipient":'
        '"ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314"}]},'
        '"message_signature":"2ca3ab38d364578749c43afed5cb0c080cf68adb86e097cc3be29ffcd84224751109f9067db83b0e'
        '81765bc04988243aafaee17b9adffe2c76397ae345a03b07",'
        '"sender":"4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732"},"updated_balances":['
        '{"account":"484b3176c63d5f37d808404af1a12c4b9649cd6f6769f35bdf5a816133623fbc","balance":855},'
        '{"account":"4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732","balance":430,'
        '"balance_lock":"d8dc544030afab2d7df13659f3821fbc13f01ce37114a426f7ac99b77d99f900"},'
        '{"account":"5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8","balance":431},'
        '{"account":"ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314","balance":434}'
        ']}'
    )
    block = Block.from_transfer_request(sample_transfer_request)
    expected_message = expected_message_template.replace(
        '<replace-with-timestamp>', block.message.timestamp.isoformat()
    ).encode('utf-8')
    assert block.message.get_normalized() == expected_message


@pytest.mark.usefixtures(
    'forced_mock_blockchain', 'get_head_block_mock', 'get_initial_account_root_file_hash_mock',
    'get_account_balance_mock'
)
def test_can_serialize_deserialize(sample_transfer_request):
    block = Block.from_transfer_request(sample_transfer_request)
    serialized_dict = block.to_dict()
    deserialized_block = Block.from_dict(serialized_dict)
    assert deserialized_block == block
    assert deserialized_block is not block
