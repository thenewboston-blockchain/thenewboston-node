import pytest

from thenewboston_node.business_logic.models import CoinTransferSignedChangeRequest


@pytest.fixture
def sample_signed_change_request_dict():
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
                'is_fee': True,
                'recipient': '5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8'
            }, {
                'amount': 4,
                'is_fee': True,
                'recipient': 'ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314'
            }]
        },
        'signature': (
            '362dc47191d5d1a33308de1f036a5e93fbaf0b05fa971d9537f954f13cd22b5ed9bee56f4701bd'
            'af9b995c47271806ba73e75d63f46084f5830cec5f5b7e9600'
        )
    }


@pytest.fixture
def sample_signed_change_request(sample_signed_change_request_dict):
    return CoinTransferSignedChangeRequest.deserialize_from_dict(sample_signed_change_request_dict)
