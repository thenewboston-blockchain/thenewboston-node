import pytest

from thenewboston_node.business_logic.models import CoinTransferSignedChangeRequest


@pytest.fixture
def sample_signed_change_request_dict(treasury_account, user_account):
    return {
        'signer':
            treasury_account,
        'message': {
            'signed_change_request_type':
                'ct',
            'balance_lock':
                treasury_account,
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
            '18cba5ba783a0e33d40bd6897da0c75e522a48527e0930d366ca59e0eb15fb55efb549242fc07dbc'
            '7196745da2dea2ac85620cb042e2120c26a809c97b53e70d'
        )
    }


@pytest.fixture
def sample_signed_change_request(sample_signed_change_request_dict):
    return CoinTransferSignedChangeRequest.deserialize_from_dict(sample_signed_change_request_dict)
