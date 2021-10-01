import pytest

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models import CoinTransferSignedChangeRequestMessage, CoinTransferTransaction


def test_get_normalized(sample_signed_change_request):
    assert sample_signed_change_request.message.get_normalized_for_cryptography() == (
        b'{"balance_lock":"4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732",'
        b'"txs":[{"amount":425,"recipient":"484b3176c63d5f37d808404af1a12c4b9649cd6f6769f35bdf5a816133623fbc"},'
        b'{"amount":1,"is_fee":true,"recipient":"5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8"},'
        b'{"amount":4,"is_fee":true,'
        b'"recipient":"ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314"}]}'
    )


def test_get_normalized_sorts_transactions():
    message = CoinTransferSignedChangeRequestMessage(
        balance_lock='',
        txs=[
            CoinTransferTransaction(amount=10, recipient='c'),
            CoinTransferTransaction(amount=10, recipient='b'),
            CoinTransferTransaction(amount=12, recipient='a'),
            CoinTransferTransaction(amount=12, recipient='a', is_fee=True),
            CoinTransferTransaction(amount=10, recipient='a', is_fee=True),
            CoinTransferTransaction(amount=10, recipient='a'),
        ]
    )
    assert message.get_normalized_for_cryptography() == (
        b'{"balance_lock":"","txs":['
        b'{"amount":10,"recipient":"a"},'
        b'{"amount":12,"recipient":"a"},'
        b'{"amount":10,"is_fee":true,"recipient":"a"},'
        b'{"amount":12,"is_fee":true,"recipient":"a"},'
        b'{"amount":10,"recipient":"b"},'
        b'{"amount":10,"recipient":"c"}'
        b']}'
    )


def test_validate(sample_coin_transfer_signed_request_message):
    sample_coin_transfer_signed_request_message.validate()


def test_validate_balance_lock(sample_coin_transfer_signed_request_message):
    sample_coin_transfer_signed_request_message.balance_lock = ''
    with pytest.raises(
        ValidationError, match='Coin transfer signed change request message balance lock must be not empty'
    ):
        sample_coin_transfer_signed_request_message.validate()

    sample_coin_transfer_signed_request_message.balance_lock = None
    with pytest.raises(
        ValidationError, match='Coin transfer signed change request message balance lock must be not empty'
    ):
        sample_coin_transfer_signed_request_message.validate()


def test_validate_transactions(sample_coin_transfer_signed_request_message: CoinTransferSignedChangeRequestMessage):
    sample_coin_transfer_signed_request_message.txs[0].amount = -1
    with pytest.raises(ValidationError, match='Coin transfer transaction amount must be greater or equal to 1'):
        sample_coin_transfer_signed_request_message.validate()

    sample_coin_transfer_signed_request_message.txs[0] = 'dummy'  # type: ignore
    with pytest.raises(
        ValidationError, match='Coin transfer signed change request message txs must be CoinTransferTransaction'
    ):
        sample_coin_transfer_signed_request_message.validate()

    sample_coin_transfer_signed_request_message.txs = 'dummy'  # type: ignore
    with pytest.raises(ValidationError, match='Coin transfer signed change request message txs must be list'):
        sample_coin_transfer_signed_request_message.validate()

    sample_coin_transfer_signed_request_message.txs = []
    with pytest.raises(ValidationError, match='Coin transfer signed change request message txs must be not empty'):
        sample_coin_transfer_signed_request_message.validate()
