import json
import tempfile

from django.test import override_settings

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.utils.blockchain_state import make_blockchain_state_from_account_root_file


@override_settings(
    BLOCKCHAIN={
        'class': 'thenewboston_node.business_logic.blockchain.memory_blockchain.MemoryBlockchain',
        'kwargs': {}
    }
)
def test_make_blockchain_state_from_account_root_file(sample_account_root_file_dict):
    BlockchainBase.clear_instance_cache()
    with tempfile.NamedTemporaryFile('w') as fp:
        json.dump(sample_account_root_file_dict, fp)
        fp.flush()
        make_blockchain_state_from_account_root_file(fp.name)

    blockchain = BlockchainBase.get_instance()

    blockchain_state = blockchain.get_last_blockchain_state()
    for key, value in sample_account_root_file_dict.items():
        account_state = blockchain_state.get_account_state(key)
        assert account_state.balance == value['balance']
        assert account_state.get_balance_lock(key) == value['balance_lock']
        if value['balance_lock'] == key:
            assert account_state.balance_lock is None

        assert account_state.node is None
