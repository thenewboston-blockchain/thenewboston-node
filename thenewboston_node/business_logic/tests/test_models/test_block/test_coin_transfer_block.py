from datetime import datetime, timedelta

import pytest

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models import (
    Block, BlockMessage, CoinTransferSignedChangeRequest, CoinTransferSignedChangeRequestMessage,
    CoinTransferTransaction
)
from thenewboston_node.business_logic.node import get_node_signing_key
from thenewboston_node.business_logic.tests.factories import add_blocks
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


def test_can_create_block_from_signed_change_request(
    file_blockchain: BlockchainBase, treasury_account, sample_signed_change_request: CoinTransferSignedChangeRequest
):
    blockchain = file_blockchain

    treasury_account_balance = blockchain.get_account_current_balance(treasury_account)

    sender = sample_signed_change_request.signer
    assert sender

    block = Block.create_from_signed_change_request(blockchain, sample_signed_change_request, get_node_signing_key())

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

    # TODO(dmu) HIGH: Improve assert for block_identifier
    assert block_message.block_identifier
    updated_account_states = block_message.updated_account_states

    assert isinstance(updated_account_states, dict)
    assert len(updated_account_states) == 4

    assert updated_account_states[sender].balance == treasury_account_balance - 425 - 4 - 1
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


def test_can_create_block_from_main_transaction(
    file_blockchain, treasury_account_key_pair: KeyPair, user_account_key_pair: KeyPair,
    primary_validator_key_pair: KeyPair, preferred_node_key_pair: KeyPair, preferred_node
):

    blockchain = file_blockchain
    treasury_account_balance = blockchain.get_account_current_balance(treasury_account_key_pair.public)

    block = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account_key_pair.public,
        amount=20,
        request_signing_key=treasury_account_key_pair.private,
        pv_signing_key=get_node_signing_key(),
        preferred_node=preferred_node,
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

    # TODO(dmu) HIGH: Implement a better assert for `block_identifier`
    assert block_message.block_identifier
    updated_account_states = block_message.updated_account_states

    assert isinstance(updated_account_states, dict)
    assert len(updated_account_states) == 4

    assert updated_account_states[treasury_account_key_pair.public].balance == treasury_account_balance - 25
    assert updated_account_states[treasury_account_key_pair.public].balance_lock

    assert updated_account_states[user_account_key_pair.public].balance == 20
    assert updated_account_states[user_account_key_pair.public].balance_lock is None

    assert updated_account_states[primary_validator_key_pair.public].balance == 4
    assert updated_account_states[primary_validator_key_pair.public].balance_lock is None

    assert updated_account_states[preferred_node_key_pair.public].balance == 1
    assert updated_account_states[preferred_node_key_pair.public].balance_lock is None

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

    assert txs_dict[preferred_node_key_pair.public].amount == 1
    assert txs_dict[preferred_node_key_pair.public].is_fee

    assert coin_transfer_signed_request_message.get_total_amount() == 25


def test_normalized_block_message(file_blockchain, sample_signed_change_request):
    expected_message_template = (
        '{"block_identifier":"967192aab18132daf231a196b6b51f6766dc61f7a12f517fd8ccadc0b5a53542",'
        '"block_number":0,"block_type":"ct","signed_change_request":{"message":'
        '{"balance_lock":"4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732",'
        '"txs":[{"amount":425,"recipient":"484b3176c63d5f37d808404af1a12c4b9649cd6f6769f35bdf5a816133623fbc"}'
        ',{"amount":1,"is_fee":true,"recipient":"5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8"}'
        ',{"amount":4,"is_fee":true,"recipient":"ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314"}'
        ']},"signature":'
        '"362dc47191d5d1a33308de1f036a5e93fbaf0b05fa971d9537f954f13cd22b5ed9bee56f4701bdaf'
        '9b995c47271806ba73e75d63f46084f5830cec5f5b7e9600","signer":'
        '"4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732"},'
        '"timestamp":"<replace-with-timestamp>","updated_account_states":'
        '{"484b3176c63d5f37d808404af1a12c4b9649cd6f6769f35bdf5a816133623fbc":'
        '{"balance":425},"4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732":'
        '{"balance":281474976710226,"balance_lock":'
        '"ff3127bdb408e5f3f4f07dd364ce719b2854dc28ee66aa7af839e46468761885"},'
        '"5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8":'
        '{"balance":1},"ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314":{"balance":4}}}'
    )

    blockchain = file_blockchain

    block = Block.create_from_signed_change_request(blockchain, sample_signed_change_request, get_node_signing_key())

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


def test_can_serialize_deserialize(file_blockchain, sample_signed_change_request):
    blockchain = file_blockchain
    block = Block.create_from_signed_change_request(blockchain, sample_signed_change_request, get_node_signing_key())
    serialized_dict = block.serialize_to_dict()
    deserialized_block = Block.deserialize_from_dict(serialized_dict)
    assert deserialized_block == block
    assert deserialized_block is not block


def test_can_duplicate_recipients(
    file_blockchain: BlockchainBase, treasury_account_key_pair: KeyPair, user_account_key_pair: KeyPair, preferred_node
):
    blockchain = file_blockchain

    block = Block.create_from_main_transaction(
        blockchain=blockchain,
        recipient=user_account_key_pair.public,
        amount=10,
        request_signing_key=treasury_account_key_pair.private,
        pv_signing_key=get_node_signing_key(),
        preferred_node=preferred_node,
    )
    blockchain.add_block(block)

    treasury_account_balance = blockchain.get_account_current_balance(treasury_account_key_pair.public)

    sender = treasury_account_key_pair.public
    recipient = user_account_key_pair.public
    message = CoinTransferSignedChangeRequestMessage(
        balance_lock=blockchain.get_account_current_balance_lock(sender),
        txs=[
            CoinTransferTransaction(recipient=recipient, amount=3),
            CoinTransferTransaction(recipient=recipient, amount=5),
        ]
    )
    request = CoinTransferSignedChangeRequest.create_from_signed_change_request_message(
        message, treasury_account_key_pair.private
    )

    block = Block.create_from_signed_change_request(blockchain, request, get_node_signing_key())

    updated_account_states = block.message.updated_account_states
    assert len(updated_account_states) == 2

    sender_account_state = block.message.get_account_state(treasury_account_key_pair.public)
    assert sender_account_state
    assert sender_account_state.balance == treasury_account_balance - 3 - 5
    assert sender_account_state.balance_lock

    recipient_account_state = block.message.get_account_state(recipient)
    assert recipient_account_state
    assert recipient_account_state.balance == 10 + 3 + 5


def test_validate_block_message_is_not_empty(
    memory_blockchain, sample_signed_change_request, primary_validator_key_pair
):
    request = sample_signed_change_request
    block = Block.create_from_signed_change_request(memory_blockchain, request, primary_validator_key_pair.private)
    block.message = None

    with pytest.raises(ValidationError, match='Block message must be not empty'):
        block.validate(memory_blockchain)


def test_validate_block_hash_matches_message_hash(
    memory_blockchain, sample_signed_change_request, primary_validator_key_pair
):
    request = sample_signed_change_request
    block = Block.create_from_signed_change_request(memory_blockchain, request, primary_validator_key_pair.private)
    block.hash = 'wrong hash'
    msg_hash = block.message.get_hash()

    with pytest.raises(ValidationError, match=f'Block hash must be equal to {msg_hash}'):
        block.validate(memory_blockchain)


def test_validate_block_signature(memory_blockchain, sample_signed_change_request, primary_validator_key_pair):
    request = sample_signed_change_request
    block = Block.create_from_signed_change_request(memory_blockchain, request, primary_validator_key_pair.private)
    block.signature = 'wrong signature'

    with pytest.raises(ValidationError, match='Message signature is invalid'):
        block.validate(memory_blockchain)


def test_validate_block_number(memory_blockchain, sample_signed_change_request, primary_validator_key_pair):
    request = sample_signed_change_request
    add_blocks(memory_blockchain, 2)
    block = Block.create_from_signed_change_request(memory_blockchain, request, primary_validator_key_pair.private)
    block.message.block_number = 99

    with pytest.raises(ValidationError, match='Block message block_number must be equal to 2'):
        block.validate(memory_blockchain)


def test_validate_account_balance_lock(memory_blockchain, sample_signed_change_request, primary_validator_key_pair):
    request = sample_signed_change_request
    add_blocks(memory_blockchain, 2)
    signer_lock = memory_blockchain.get_account_current_balance_lock(account=request.signer)
    block = Block.create_from_signed_change_request(memory_blockchain, request, primary_validator_key_pair.private)
    block.message.signed_change_request.balance_lock = 'wrong lock'

    with pytest.raises(
        ValidationError,
        match=f'Coin transfer signed change request message balance_lock must be equal to {signer_lock}'
    ):
        block.validate(memory_blockchain)
