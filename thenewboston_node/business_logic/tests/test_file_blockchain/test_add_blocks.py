from unittest.mock import patch

from thenewboston_node.business_logic.tests.factories import add_blocks

# Main purpose of this file is performance optimization and debugging


def test_add_one_block(file_blockchain):
    add_blocks(file_blockchain, 1, file_blockchain._test_treasury_account_key_pair.private)


def test_add_two_blocks(file_blockchain):
    add_blocks(file_blockchain, 2, file_blockchain._test_treasury_account_key_pair.private)


def test_add_four_blocks(file_blockchain):
    add_blocks(file_blockchain, 4, file_blockchain._test_treasury_account_key_pair.private)


def test_add_eight_blocks(file_blockchain):
    add_blocks(file_blockchain, 8, file_blockchain._test_treasury_account_key_pair.private)


def test_add_blocks_with_frequent_snapshots(file_blockchain):
    with patch.object(file_blockchain, 'snapshot_period_in_blocks', 3):
        add_blocks(file_blockchain, 16, file_blockchain._test_treasury_account_key_pair.private)


def test_add_blocks_with_normal_snapshots(file_blockchain):
    add_blocks(file_blockchain, 16, file_blockchain._test_treasury_account_key_pair.private)
