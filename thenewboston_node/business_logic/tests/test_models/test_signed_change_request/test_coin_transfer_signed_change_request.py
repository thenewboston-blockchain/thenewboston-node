import copy
from unittest.mock import patch

import pytest

from thenewboston_node.business_logic.blockchain.mock_blockchain import MockBlockchain
from thenewboston_node.business_logic.exceptions import InvalidMessageSignatureError, ValidationError
from thenewboston_node.business_logic.models import (
    CoinTransferSignedChangeRequest, CoinTransferSignedChangeRequestMessage, CoinTransferTransaction
)


def test_can_create_signed_change_request_from_dict(sample_signed_change_request_dict):
    signed_change_request = CoinTransferSignedChangeRequest.deserialize_from_dict(sample_signed_change_request_dict)
    assert signed_change_request.signer == sample_signed_change_request_dict['signer']
    assert signed_change_request.message.balance_lock == sample_signed_change_request_dict['message']['balance_lock']

    txs_dict = sample_signed_change_request_dict['message']['txs']
    for index, tx in enumerate(signed_change_request.message.txs):
        tx_dict = txs_dict[index]
        assert tx.amount == tx_dict['amount']
        assert tx.recipient == tx_dict['recipient']
        assert tx.fee == tx_dict.get('fee', False)

    assert signed_change_request.signature == sample_signed_change_request_dict['signature']


def test_validate_signature(sample_signed_change_request):
    sample_signed_change_request.validate_signature()


def test_validate_signature_raises(sample_signed_change_request):
    sample_signed_change_request_copy = copy.deepcopy(sample_signed_change_request)
    sample_signed_change_request_copy.signature = 'invalid' + sample_signed_change_request_copy.signature[
        len('invalid'):]
    with pytest.raises(InvalidMessageSignatureError):
        sample_signed_change_request_copy.validate_signature()

    sample_signed_change_request_copy = copy.deepcopy(sample_signed_change_request)
    sample_signed_change_request_copy.signature = 'aaaaa' + sample_signed_change_request_copy.signature[5:]
    with pytest.raises(InvalidMessageSignatureError):
        sample_signed_change_request_copy.validate_signature()


def test_validate_amount(forced_mock_blockchain, sample_signed_change_request):
    with patch.object(MockBlockchain, 'get_account_balance', return_value=425 + 1 + 4):
        sample_signed_change_request.validate_amount(forced_mock_blockchain, 0)


def test_validate_amount_raises(forced_mock_blockchain, sample_signed_change_request):
    sample_signed_change_request_copy = copy.deepcopy(sample_signed_change_request)
    with patch.object(MockBlockchain, 'get_account_balance', return_value=0):
        with pytest.raises(
            ValidationError, match='Coin transfer signed change request singer balance must be greater than zero'
        ):
            sample_signed_change_request_copy.validate_amount(forced_mock_blockchain, 0)

    sample_signed_change_request_copy = copy.deepcopy(sample_signed_change_request)
    with patch.object(MockBlockchain, 'get_account_balance', return_value=425 + 1 + 4 - 1):
        with pytest.raises(
            ValidationError, match='Coin transfer signed change request total amount must be less or equal to 429'
        ):
            sample_signed_change_request_copy.validate_amount(forced_mock_blockchain, -100)


def test_validate_balance_lock(forced_mock_blockchain, sample_signed_change_request):
    with patch.object(
        MockBlockchain,
        'get_account_balance_lock',
        return_value='4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732'
    ):
        sample_signed_change_request.validate_balance_lock(forced_mock_blockchain, -100)


def test_validate_balance_lock_raises(forced_mock_blockchain, sample_signed_change_request):
    with patch.object(
        MockBlockchain,
        'get_account_balance_lock',
        return_value='1cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb'
    ):
        with pytest.raises(
            ValidationError,
            match='Coin transfer signed change request message balance_lock must be equal to '
            '1cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb'
        ):
            sample_signed_change_request.validate_balance_lock(forced_mock_blockchain, -100)


def test_validate(forced_mock_blockchain, sample_signed_change_request):
    with patch.object(MockBlockchain, 'get_account_balance', return_value=425 + 1 + 4):
        with patch.object(
            MockBlockchain,
            'get_account_balance_lock',
            return_value='4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732'
        ):
            sample_signed_change_request.validate(forced_mock_blockchain, -100)


def test_invalid_sender(forced_mock_blockchain, sample_signed_change_request):
    sample_signed_change_request.signer = ''
    with pytest.raises(ValidationError, match='Signer must be not empty'):
        sample_signed_change_request.validate(forced_mock_blockchain, -100)

    sample_signed_change_request.signer = None
    with pytest.raises(ValidationError, match='Signer must be not empty'):
        sample_signed_change_request.validate(forced_mock_blockchain, -100)

    sample_signed_change_request.signer = 12
    with pytest.raises(ValidationError, match='Signer must be string'):
        sample_signed_change_request.validate(forced_mock_blockchain, -100)


def test_invalid_signed_change_request_for_signature(forced_mock_blockchain, sample_signed_change_request):
    sample_signed_change_request_copy = copy.deepcopy(sample_signed_change_request)
    sample_signed_change_request_copy.signature = 'aaaaa' + sample_signed_change_request_copy.signature[5:]
    with pytest.raises(InvalidMessageSignatureError):
        sample_signed_change_request_copy.validate(forced_mock_blockchain, -100)


def test_invalid_signed_change_request_for_amount(forced_mock_blockchain, sample_signed_change_request):
    with patch.object(MockBlockchain, 'get_account_balance', return_value=425 + 1 + 4 - 1):
        with pytest.raises(
            ValidationError, match='Coin transfer signed change request total amount must be less or equal to 429'
        ):
            sample_signed_change_request.validate(forced_mock_blockchain, -100)


def test_invalid_signed_change_request_for_balance_lock(forced_mock_blockchain, sample_signed_change_request):
    with patch.object(
        MockBlockchain,
        'get_account_balance_lock',
        return_value='1cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb'
    ):
        with pytest.raises(
            ValidationError,
            match='Coin transfer signed change request message balance_lock must be equal to '
            '1cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb'
        ):
            sample_signed_change_request.validate_balance_lock(forced_mock_blockchain, -100)


def test_can_create_from_coin_transfer_signed_request_message(user_account_key_pair):
    message = CoinTransferSignedChangeRequestMessage(
        balance_lock='1cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb',
        txs=[
            CoinTransferTransaction(
                amount=10, recipient='0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb'
            )
        ]
    )
    request = CoinTransferSignedChangeRequest.create_from_signed_change_request_message(
        message, user_account_key_pair.private
    )
    assert request.signer == user_account_key_pair.public
    assert request.message == message
    assert request.message is not message
    assert request.signature
    request.validate_signature()
