from thenewboston_node.business_logic.models.transaction import Transaction
from thenewboston_node.business_logic.models.transfer_request_message import TransferRequestMessage


def test_get_normalized(sample_transfer_request):
    assert sample_transfer_request.message.get_normalized() == (
        b'{"balance_lock":"4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732",'
        b'"txs":[{"amount":425,"recipient":"484b3176c63d5f37d808404af1a12c4b9649cd6f6769f35bdf5a816133623fbc"},'
        b'{"amount":1,"fee":"NODE","recipient":"5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8"},'
        b'{"amount":4,"fee":"PRIMARY_VALIDATOR",'
        b'"recipient":"ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314"}]}'
    )


def test_get_normalized_sorts_transactions():
    message = TransferRequestMessage(
        balance_lock='',
        txs=[
            Transaction(amount=1, recipient='c'),
            Transaction(amount=1, recipient='b'),
            Transaction(amount=1, recipient='a')
        ]
    )
    assert message.get_normalized() == (
        b'{"balance_lock":"","txs":[{"amount":1,"recipient":"a"},{"amount":1,"recipient":"b"},'
        b'{"amount":1,"recipient":"c"}]}'
    )
