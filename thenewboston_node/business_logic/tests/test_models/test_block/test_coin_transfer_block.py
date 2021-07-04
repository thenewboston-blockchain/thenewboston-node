from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from thenewboston_node.business_logic.blockchain.mock_blockchain import MockBlockchain
from thenewboston_node.business_logic.models import (
    Block, BlockMessage, CoinTransferSignedChangeRequest, CoinTransferSignedChangeRequestMessage,
    CoinTransferTransaction
)
from thenewboston_node.business_logic.node import get_node_signing_key
from thenewboston_node.core.utils import baker
from thenewboston_node.core.utils.cryptography import KeyPair, derive_public_key


def test_can_serialize_coin_transfer_block():
    signed_change_request = baker.make(CoinTransferSignedChangeRequest)
    block_message = baker.make(BlockMessage, block_type='ct', signed_change_request=signed_change_request)
    block = baker.make(Block, message=block_message)
    block_dict = block.serialize_to_dict()
    assert isinstance(block_dict, dict)
    assert block_dict.keys() == {'signer', 'message', 'hash', 'signature'}
    assert isinstance(block_dict['signer'], str)
    assert isinstance(block_dict['message'], dict)
    assert isinstance(block_dict['hash'], str)
    assert isinstance(block_dict['signature'], str)

    block_message = block_dict['message']
    assert block_message.keys() == {
        'block_type', 'signed_change_request', 'timestamp', 'block_number', 'block_identifier',
        'updated_account_states'
    }
    assert block_message['block_type'] == 'ct'
    assert isinstance(block_message['signed_change_request'], dict)
    assert isinstance(block_message['timestamp'], str)
    assert isinstance(block_message['block_number'], int)
    assert isinstance(block_message['block_identifier'], str)
    assert isinstance(block_message['updated_account_states'], dict)

    signed_change_request = block_message['signed_change_request']
    assert signed_change_request.keys() == {'signer', 'message', 'signature'}
    assert isinstance(signed_change_request['signer'], str)
    assert isinstance(signed_change_request['message'], dict)
    assert isinstance(signed_change_request['signature'], str)

    signed_change_request_message = signed_change_request['message']
    assert signed_change_request_message.keys() == {'balance_lock', 'txs'}
    assert isinstance(signed_change_request_message['balance_lock'], str)
    assert isinstance(signed_change_request_message['txs'], list)
    for transaction in signed_change_request_message['txs']:
        assert isinstance(transaction, dict)
        if 'is_fee' in transaction:
            assert transaction.keys() == {'recipient', 'amount', 'is_fee', 'memo'}
            assert isinstance(transaction['is_fee'], bool)
        else:
            assert transaction.keys() == {'recipient', 'amount', 'memo'}

        assert isinstance(transaction['recipient'], str)
        assert isinstance(transaction['amount'], int)
        assert isinstance(transaction['memo'], str)

    updated_account_states = block_message['updated_account_states']
    for key, value in updated_account_states.items():
        assert isinstance(key, str)
        assert isinstance(value, dict)
        assert value.keys() == {'balance', 'balance_lock', 'node', 'primary_validator_schedule'}
        assert isinstance(value['balance'], int)
        assert isinstance(value['balance_lock'], str)
        assert isinstance(value['node'], dict)
        node = value['node']
        assert 'identifier' not in node
        assert isinstance(node['network_addresses'], list)
        assert isinstance(node['fee_amount'], int)
        assert isinstance(node['fee_account'], str)


@pytest.mark.usefixtures('get_next_block_identifier_mock', 'get_next_block_number_mock')
def test_can_create_block_from_signed_change_request(
    forced_mock_blockchain, sample_signed_change_request: CoinTransferSignedChangeRequest
):

    sender = sample_signed_change_request.signer
    assert sender

    def get_account_balance(self, account, on_block_number):
        return 450 if account == sender else 0

    with patch.object(MockBlockchain, 'get_account_balance', new=get_account_balance):
        block = Block.create_from_signed_change_request(
            forced_mock_blockchain, sample_signed_change_request, get_node_signing_key()
        )

    assert block.message
    assert block.hash
    assert block.signature
    block.validate_signature()
    assert block.signer
    assert block.signer == derive_public_key(get_node_signing_key())

    block_message = block.message

    signed_change_request = block_message.signed_change_request
    assert signed_change_request == sample_signed_change_request
    assert signed_change_request is not sample_signed_change_request  # test that a copy of it was made

    assert isinstance(block_message.timestamp, datetime)
    assert block_message.timestamp.tzinfo is None
    assert block_message.timestamp - datetime.utcnow() < timedelta(seconds=1)

    assert block_message.block_number == 0
    assert block_message.block_identifier == 'next-block-identifier'
    updated_account_states = block_message.updated_account_states

    assert isinstance(updated_account_states, dict)
    assert len(updated_account_states) == 4

    assert updated_account_states[sender].balance == 450 - 425 - 4 - 1
    assert updated_account_states[sender].balance_lock

    assert updated_account_states['484b3176c63d5f37d808404af1a12c4b9649cd6f6769f35bdf5a816133623fbc'].balance == 425
    assert updated_account_states['484b3176c63d5f37d808404af1a12c4b9649cd6f6769f35bdf5a816133623fbc'
                                  ].balance_lock is None

    assert updated_account_states['ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314'].balance == 4
    assert updated_account_states['ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314'
                                  ].balance_lock is None

    assert updated_account_states['5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8'].balance == 1
    assert updated_account_states['5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8'
                                  ].balance_lock is None


@pytest.mark.usefixtures(
    'forced_mock_network', 'get_next_block_identifier_mock', 'get_next_block_number_mock', 'get_account_state_mock',
    'get_account_lock_mock', 'get_primary_validator_mock', 'get_preferred_node_mock'
)
def test_can_create_block_from_main_transaction(
    forced_mock_blockchain, treasury_account_key_pair: KeyPair, user_account_key_pair: KeyPair,
    primary_validator_key_pair: KeyPair, node_key_pair: KeyPair
):

    def get_account_balance(self, account, on_block_number):
        return 430 if account == treasury_account_key_pair.public else 0

    with patch.object(MockBlockchain, 'get_account_balance', new=get_account_balance):
        block = Block.create_from_main_transaction(
            blockchain=forced_mock_blockchain,
            recipient=user_account_key_pair.public,
            amount=20,
            request_signing_key=treasury_account_key_pair.private,
            pv_signing_key=get_node_signing_key(),
        )

    # Assert block
    assert block.message
    assert block.hash
    assert block.signature

    block.validate_signature()
    assert block.signer
    assert block.signer == derive_public_key(get_node_signing_key())

    # Assert block.message
    block_message = block.message
    assert block_message
    assert isinstance(block_message.timestamp, datetime)
    assert block_message.timestamp.tzinfo is None
    assert block_message.timestamp - datetime.utcnow() < timedelta(seconds=1)

    assert block_message.block_number == 0
    assert block_message.block_identifier == 'next-block-identifier'
    updated_account_states = block_message.updated_account_states

    assert isinstance(updated_account_states, dict)
    assert len(updated_account_states) == 4

    assert updated_account_states[treasury_account_key_pair.public].balance == 430 - 25
    assert updated_account_states[treasury_account_key_pair.public].balance_lock

    assert updated_account_states[user_account_key_pair.public].balance == 20
    assert updated_account_states[user_account_key_pair.public].balance_lock is None

    assert updated_account_states[primary_validator_key_pair.public].balance == 4
    assert updated_account_states[primary_validator_key_pair.public].balance_lock is None

    assert updated_account_states[node_key_pair.public].balance == 1
    assert updated_account_states[node_key_pair.public].balance_lock is None

    # Assert block_message.signed_change_request
    signed_change_request = block_message.signed_change_request
    assert signed_change_request.signer == treasury_account_key_pair.public
    assert signed_change_request.signature

    # Assert block_message.signed_change_request.message
    coin_transfer_signed_request_message = signed_change_request.message
    assert isinstance(coin_transfer_signed_request_message, CoinTransferSignedChangeRequestMessage)
    assert coin_transfer_signed_request_message.balance_lock
    assert len(coin_transfer_signed_request_message.txs) == 3
    txs_dict = {tx.recipient: tx for tx in coin_transfer_signed_request_message.txs}
    assert len(txs_dict) == 3

    assert txs_dict[user_account_key_pair.public].amount == 20
    assert txs_dict[user_account_key_pair.public].is_fee is False

    assert txs_dict[primary_validator_key_pair.public].amount == 4
    assert txs_dict[primary_validator_key_pair.public].is_fee

    assert txs_dict[node_key_pair.public].amount == 1
    assert txs_dict[node_key_pair.public].is_fee

    assert coin_transfer_signed_request_message.get_total_amount() == 25


@pytest.mark.usefixtures('get_next_block_identifier_mock', 'get_next_block_number_mock', 'get_account_state_mock')
def test_normalized_block_message(forced_mock_blockchain, sample_signed_change_request):
    expected_message_template = (
        '{'
        '"block_identifier":"next-block-identifier",'
        '"block_number":0,'
        '"block_type":"ct",'
        '"signed_change_request":'
        '{"message":{"balance_lock":'
        '"4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732",'
        '"txs":'
        '[{"amount":425,"recipient":"484b3176c63d5f37d808404af1a12c4b9649cd6f6769f35bdf5a816133623fbc"},'
        '{"amount":1,"is_fee":true,"recipient":"5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8"},'
        '{"amount":4,"is_fee":true,"recipient":'
        '"ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314"}]},'
        '"signature":"362dc47191d5d1a33308de1f036a5e93fbaf0b05fa971d9537f954f13cd22b5ed9bee56f4701bd'
        'af9b995c47271806ba73e75d63f46084f5830cec5f5b7e9600",'
        '"signer":"4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732"},'
        '"timestamp":"<replace-with-timestamp>",'
        '"updated_account_states":{'
        '"484b3176c63d5f37d808404af1a12c4b9649cd6f6769f35bdf5a816133623fbc":{"balance":425},'
        '"4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732":'
        '{'
        '"balance":20,'
        '"balance_lock":"ff3127bdb408e5f3f4f07dd364ce719b2854dc28ee66aa7af839e46468761885"'
        '},'
        '"5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8":{"balance":1},'
        '"ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314":{"balance":4}'
        '}'
        '}'
    )

    def get_account_balance(self, account, on_block_number):
        return 450 if account == sample_signed_change_request.signer else 0

    with patch.object(MockBlockchain, 'get_account_balance', new=get_account_balance):
        block = Block.create_from_signed_change_request(
            forced_mock_blockchain, sample_signed_change_request, get_node_signing_key()
        )

    expected_message = expected_message_template.replace(
        '<replace-with-timestamp>', block.message.timestamp.isoformat()
    ).encode('utf-8')
    assert block.message.get_normalized() == expected_message


def test_can_serialize_deserialize_coin_transfer_signed_change_request_message():
    message = baker.make(CoinTransferSignedChangeRequestMessage)
    serialized = message.serialize_to_dict()
    deserialized = CoinTransferSignedChangeRequestMessage.deserialize_from_dict(serialized)
    assert deserialized == message
    assert deserialized is not message


@pytest.mark.usefixtures('get_next_block_identifier_mock', 'get_next_block_number_mock', 'get_account_state_mock')
def test_can_serialize_deserialize(forced_mock_blockchain, sample_signed_change_request):
    block = Block.create_from_signed_change_request(
        forced_mock_blockchain, sample_signed_change_request, get_node_signing_key()
    )
    serialized_dict = block.serialize_to_dict()
    deserialized_block = Block.deserialize_from_dict(serialized_dict)
    assert deserialized_block == block
    assert deserialized_block is not block


@pytest.mark.usefixtures('get_next_block_identifier_mock', 'get_next_block_number_mock', 'get_account_lock_mock')
def test_can_duplicate_recipients(
    forced_mock_blockchain: MockBlockchain, treasury_account_key_pair: KeyPair, user_account_key_pair: KeyPair
):

    def get_account_balance(self, account, on_block_number):
        return 430 if account == treasury_account_key_pair.public else 10

    sender = treasury_account_key_pair.public
    recipient = user_account_key_pair.public
    message = CoinTransferSignedChangeRequestMessage(
        balance_lock=forced_mock_blockchain.get_account_current_balance_lock(sender),
        txs=[
            CoinTransferTransaction(recipient=recipient, amount=3),
            CoinTransferTransaction(recipient=recipient, amount=5),
        ]
    )
    request = CoinTransferSignedChangeRequest.create_from_signed_change_request_message(
        message, treasury_account_key_pair.private
    )

    with patch.object(MockBlockchain, 'get_account_balance', new=get_account_balance):
        block = Block.create_from_signed_change_request(forced_mock_blockchain, request, get_node_signing_key())

    updated_account_states = block.message.updated_account_states
    assert len(updated_account_states) == 2

    sender_account_state = block.message.get_account_state(treasury_account_key_pair.public)
    assert sender_account_state
    assert sender_account_state.balance == 430 - 3 - 5
    assert sender_account_state.balance_lock

    recipient_account_state = block.message.get_account_state(user_account_key_pair.public)
    assert recipient_account_state
    assert recipient_account_state.balance == 10 + 3 + 5


@pytest.mark.skip('Not implemented yet')
def test_validate_block():
    raise NotImplementedError()
