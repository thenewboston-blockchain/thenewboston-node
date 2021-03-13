import pytest

from thenewboston_node.business_logic.models.transfer_request import TransferRequest


@pytest.fixture
def sample_transfer_request_dict():
    return {
        'sender':
            '0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb',
        'message': {
            'balance_key':
                '0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb',
            'txs': [{
                'amount': 425,
                'recipient': '484b3176c63d5f37d808404af1a12c4b9649cd6f6769f35bdf5a816133623fbc'
            }, {
                'amount': 1,
                'fee': 'BANK',
                'recipient': '5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8'
            }, {
                'amount': 4,
                'fee': 'PRIMARY_VALIDATOR',
                'recipient': 'ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314'
            }]
        },
        'message_signature': (
            '2c2aae162c0de7d7c66856a1728e06c26fe1732a8073721ca0cf6d22f868be07158f7256ba02e34eb913'
            'aea0f3c16cc135bacc3631a74f97b1fb7a3463059707'
        )
    }


@pytest.fixture
def sample_transfer_request(sample_transfer_request_dict):
    return TransferRequest.from_dict(sample_transfer_request_dict)
