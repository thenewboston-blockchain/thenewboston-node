import copy
from unittest.mock import patch

from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
from thenewboston_node.business_logic.models.transfer_request import TransferRequest


def test_can_create_transfer_request_from_dict(sample_transfer_request_dict):
    transfer_request = TransferRequest.from_dict(sample_transfer_request_dict)
    assert transfer_request.sender == sample_transfer_request_dict['sender']
    assert transfer_request.message.balance_key == sample_transfer_request_dict['message']['balance_key']

    txs_dict = sample_transfer_request_dict['message']['txs']
    for index, tx in enumerate(transfer_request.message.txs):
        tx_dict = txs_dict[index]
        assert tx.amount == tx_dict['amount']
        assert tx.recipient == tx_dict['recipient']
        assert tx.fee == tx_dict.get('fee')

    assert transfer_request.signature == sample_transfer_request_dict['signature']


def test_is_signature_valid(sample_transfer_request):
    assert sample_transfer_request.is_signature_valid()


def test_is_signature_valid_negative(sample_transfer_request):
    sample_transfer_request_copy = copy.deepcopy(sample_transfer_request)
    sample_transfer_request_copy.signature = 'invalid' + sample_transfer_request_copy.signature[len('invalid'):]
    assert not sample_transfer_request_copy.is_signature_valid()
    assert sample_transfer_request_copy.validation_errors == ['Message signature is invalid']

    sample_transfer_request_copy = copy.deepcopy(sample_transfer_request)
    sample_transfer_request_copy.signature = 'aaaaa' + sample_transfer_request_copy.signature[5:]
    assert not sample_transfer_request_copy.is_signature_valid()
    assert sample_transfer_request_copy.validation_errors == ['Message signature is invalid']


def test_is_amount_valid(sample_transfer_request):
    with patch.object(FileBlockchain, 'get_account_balance', return_value=425 + 1 + 4):
        assert sample_transfer_request.is_amount_valid()


def test_is_amount_valid_negative(sample_transfer_request):
    sample_transfer_request_copy = copy.deepcopy(sample_transfer_request)
    with patch.object(FileBlockchain, 'get_account_balance', return_value=None):
        assert not sample_transfer_request_copy.is_amount_valid()
        assert sample_transfer_request_copy.validation_errors == ['Account balance is not found']

    sample_transfer_request_copy = copy.deepcopy(sample_transfer_request)
    with patch.object(FileBlockchain, 'get_account_balance', return_value=425 + 1 + 4 - 1):
        assert not sample_transfer_request_copy.is_amount_valid()
        assert sample_transfer_request_copy.validation_errors == [
            'Transaction total amount is greater than account balance'
        ]


def test_is_balance_key_valid(sample_transfer_request):
    with patch.object(
        FileBlockchain,
        'get_account_balance_lock',
        return_value='0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb'
    ):
        assert sample_transfer_request.is_balance_key_valid()


def test_is_balance_key_valid_negative(sample_transfer_request):
    with patch.object(
        FileBlockchain,
        'get_account_balance_lock',
        return_value='1cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb'
    ):
        assert not sample_transfer_request.is_balance_key_valid()
        assert sample_transfer_request.validation_errors == ['Balance key does not match balance lock']


def test_is_valid(sample_transfer_request):
    with patch.object(FileBlockchain, 'get_account_balance', return_value=425 + 1 + 4):
        with patch(
            'thenewboston_node.business_logic.blockchain.file_blockchain.get_account_balance_lock',
            return_value='0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb'
        ):
            assert sample_transfer_request.is_valid()


def test_invalid_transfer_request_for_signature(sample_transfer_request):
    sample_transfer_request_copy = copy.deepcopy(sample_transfer_request)
    sample_transfer_request_copy.signature = 'aaaaa' + sample_transfer_request_copy.signature[5:]
    assert not sample_transfer_request_copy.is_valid()
    assert sample_transfer_request_copy.validation_errors == ['Message signature is invalid']


def test_invalid_transfer_request_for_amount(sample_transfer_request):
    with patch.object(FileBlockchain, 'get_account_balance', return_value=425 + 1 + 4 - 1):
        assert not sample_transfer_request.is_valid()
        assert sample_transfer_request.validation_errors == [
            'Transaction total amount is greater than account balance'
        ]


def test_invalid_transfer_request_for_balance_key(sample_transfer_request):
    with patch.object(
        FileBlockchain,
        'get_account_balance_lock',
        return_value='1cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb'
    ):
        assert not sample_transfer_request.is_balance_key_valid()
        assert sample_transfer_request.validation_errors == ['Balance key does not match balance lock']
