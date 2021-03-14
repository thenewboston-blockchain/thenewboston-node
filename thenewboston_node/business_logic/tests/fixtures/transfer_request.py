import pytest

from thenewboston_node.business_logic.models.transfer_request import TransferRequest


@pytest.fixture
def sample_transfer_request_dict():
    return {
        'sender':
            '4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732',
        'message': {
            'balance_lock':
                '4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732',
            'txs': [{
                'amount': 425,
                'recipient': '484b3176c63d5f37d808404af1a12c4b9649cd6f6769f35bdf5a816133623fbc'
            }, {
                'amount': 1,
                'fee': 'NODE',
                'recipient': '5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8'
            }, {
                'amount': 4,
                'fee': 'PRIMARY_VALIDATOR',
                'recipient': 'ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314'
            }]
        },
        'message_signature': (
            '2ca3ab38d364578749c43afed5cb0c080cf68adb86e097cc3be29ffcd84224751109f9067db83b0e'
            '81765bc04988243aafaee17b9adffe2c76397ae345a03b07'
        )
    }


@pytest.fixture
def sample_transfer_request(sample_transfer_request_dict):
    return TransferRequest.from_dict(sample_transfer_request_dict)
