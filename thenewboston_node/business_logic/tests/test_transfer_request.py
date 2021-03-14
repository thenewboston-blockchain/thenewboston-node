import copy
from unittest.mock import patch

import pytest

from thenewboston_node.business_logic.blockchain.mock_blockchain import MockBlockchain
from thenewboston_node.business_logic.models.transaction import Transaction
from thenewboston_node.business_logic.models.transfer_request import TransferRequest
from thenewboston_node.business_logic.models.transfer_request_message import TransferRequestMessage


def test_can_create_transfer_request_from_dict(sample_transfer_request_dict):
    transfer_request = TransferRequest.from_dict(sample_transfer_request_dict)
    assert transfer_request.sender == sample_transfer_request_dict['sender']
    assert transfer_request.message.balance_lock == sample_transfer_request_dict['message']['balance_lock']

    txs_dict = sample_transfer_request_dict['message']['txs']
    for index, tx in enumerate(transfer_request.message.txs):
        tx_dict = txs_dict[index]
        assert tx.amount == tx_dict['amount']
        assert tx.recipient == tx_dict['recipient']
        assert tx.fee == tx_dict.get('fee')

    assert transfer_request.message_signature == sample_transfer_request_dict['message_signature']


def test_is_signature_valid(sample_transfer_request):
    assert sample_transfer_request.is_signature_valid()


def test_is_signature_valid_negative(sample_transfer_request):
    sample_transfer_request_copy = copy.deepcopy(sample_transfer_request)
    sample_transfer_request_copy.message_signature = 'invalid' + sample_transfer_request_copy.message_signature[
        len('invalid'):]
    assert not sample_transfer_request_copy.is_signature_valid()
    assert sample_transfer_request_copy.validation_errors == ['Message signature is invalid']

    sample_transfer_request_copy = copy.deepcopy(sample_transfer_request)
    sample_transfer_request_copy.message_signature = 'aaaaa' + sample_transfer_request_copy.message_signature[5:]
    assert not sample_transfer_request_copy.is_signature_valid()
    assert sample_transfer_request_copy.validation_errors == ['Message signature is invalid']


@pytest.mark.usefixtures('use_mock_blockchain')
def test_is_amount_valid(sample_transfer_request):
    with patch.object(MockBlockchain, 'get_account_balance', return_value=425 + 1 + 4):
        assert sample_transfer_request.is_amount_valid()


@pytest.mark.usefixtures('use_mock_blockchain')
def test_is_amount_valid_negative(sample_transfer_request):
    sample_transfer_request_copy = copy.deepcopy(sample_transfer_request)
    with patch.object(MockBlockchain, 'get_account_balance', return_value=None):
        assert not sample_transfer_request_copy.is_amount_valid()
        assert sample_transfer_request_copy.validation_errors == ['Account balance is not found']

    sample_transfer_request_copy = copy.deepcopy(sample_transfer_request)
    with patch.object(MockBlockchain, 'get_account_balance', return_value=425 + 1 + 4 - 1):
        assert not sample_transfer_request_copy.is_amount_valid()
        assert sample_transfer_request_copy.validation_errors == [
            'Transaction total amount is greater than account balance'
        ]


@pytest.mark.usefixtures('use_mock_blockchain')
def test_is_balance_lock_valid(sample_transfer_request):
    with patch.object(
        MockBlockchain,
        'get_account_balance_lock',
        return_value='4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732'
    ):
        assert sample_transfer_request.is_balance_lock_valid()


@pytest.mark.usefixtures('use_mock_blockchain')
def test_is_balance_lock_valid_negative(sample_transfer_request):
    with patch.object(
        MockBlockchain,
        'get_account_balance_lock',
        return_value='1cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb'
    ):
        assert not sample_transfer_request.is_balance_lock_valid()
        assert sample_transfer_request.validation_errors == ['Balance key does not match balance lock']


@pytest.mark.usefixtures('use_mock_blockchain')
def test_is_valid(sample_transfer_request):
    with patch.object(MockBlockchain, 'get_account_balance', return_value=425 + 1 + 4):
        with patch.object(
            MockBlockchain,
            'get_account_balance_lock',
            return_value='4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732'
        ):
            assert sample_transfer_request.is_valid()


def test_invalid_transfer_request_for_signature(sample_transfer_request):
    sample_transfer_request_copy = copy.deepcopy(sample_transfer_request)
    sample_transfer_request_copy.message_signature = 'aaaaa' + sample_transfer_request_copy.message_signature[5:]
    assert not sample_transfer_request_copy.is_valid()
    assert sample_transfer_request_copy.validation_errors == ['Message signature is invalid']


@pytest.mark.usefixtures('use_mock_blockchain')
def test_invalid_transfer_request_for_amount(sample_transfer_request):
    with patch.object(MockBlockchain, 'get_account_balance', return_value=425 + 1 + 4 - 1):
        assert not sample_transfer_request.is_valid()
        assert sample_transfer_request.validation_errors == [
            'Transaction total amount is greater than account balance'
        ]


@pytest.mark.usefixtures('use_mock_blockchain')
def test_invalid_transfer_request_for_balance_lock(sample_transfer_request):
    with patch.object(
        MockBlockchain,
        'get_account_balance_lock',
        return_value='1cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb'
    ):
        assert not sample_transfer_request.is_balance_lock_valid()
        assert sample_transfer_request.validation_errors == ['Balance key does not match balance lock']


def test_can_create_from_transfer_request_message(user_account_key_pair):
    message = TransferRequestMessage(
        balance_lock='1cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb',
        txs=[Transaction(amount=10, recipient='0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb')]
    )
    request = TransferRequest.from_transfer_request_message(message, user_account_key_pair.private)
    assert request.sender == user_account_key_pair.public
    assert request.message == message
    assert request.message is not message
    assert request.message_signature
    assert request.is_signature_valid()
