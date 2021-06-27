from thenewboston_node.business_logic.models.blockchain_state import BlockchainState


def test_from_account_root_file(sample_account_root_file_dict):
    blockchain_state = BlockchainState.from_account_root_file(sample_account_root_file_dict)
    for key, value in sample_account_root_file_dict.items():
        account_state = blockchain_state.get_account_state(key)
        assert account_state.balance == value['balance']
        assert account_state.get_balance_lock(key) == value['balance_lock']
        if value['balance_lock'] == key:
            assert account_state.balance_lock is None

        assert account_state.node is None
