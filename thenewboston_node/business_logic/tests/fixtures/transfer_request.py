import pytest

from thenewboston_node.business_logic.models import CoinTransferSignedChangeRequest


@pytest.fixture
def sample_transfer_request_dict():
    return {
        'signer':
            '4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732',
        'message': {
            'balance_lock':
                '4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732',
            'txs': [{
                'amount': 425,
                'recipient': '484b3176c63d5f37d808404af1a12c4b9649cd6f6769f35bdf5a816133623fbc'
            }, {
                'amount': 1,
                'fee': True,
                'recipient': '5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8'
            }, {
                'amount': 4,
                'fee': True,
                'recipient': 'ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314'
            }]
        },
        'signature': (
            '8c1b5719745cdc81e71905e874c1f1fb938d941dd6d03ddc6dc39fc60ca42dcb8a17bb2e721c3f2a'
            '128a2dff35a3b0f843efe78893adde78a27192ca54212a08'
        )
    }


@pytest.fixture
def sample_transfer_request(sample_transfer_request_dict):
    return CoinTransferSignedChangeRequest.from_dict(sample_transfer_request_dict)
