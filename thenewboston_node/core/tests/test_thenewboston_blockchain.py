from functools import partial
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command

from thenewboston_node.business_logic.blockchain.base import BlockchainBase


class TestThenewbostonBlockchain:
    run_command = partial(call_command, 'blockchain')

    def test_get_block(self, file_blockchain_with_three_block_chunks):
        with patch.object(
            BlockchainBase, 'get_instance', return_value=file_blockchain_with_three_block_chunks
        ) as mock_method:
            out = StringIO()
            self.run_command('get-block', 2, stdout=out)
            assert "'block_number': 2" in out.getvalue()
        mock_method.assert_called_once()

    def test_get_block_when_block_is_missed(self, file_blockchain_with_three_block_chunks):
        with patch.object(
            BlockchainBase, 'get_instance', return_value=file_blockchain_with_three_block_chunks
        ) as mock_method:
            out = StringIO()
            self.run_command('get-block', 10, stdout=out)
            assert out.getvalue() == ''
        mock_method.assert_called_once()

    def test_get_blocks(self, file_blockchain_with_three_block_chunks):
        with patch.object(
            BlockchainBase, 'get_instance', return_value=file_blockchain_with_three_block_chunks
        ) as mock_method:
            out = StringIO()
            self.run_command('get-blocks', 2, 3, stdout=out)
            assert "'block_number': 2" in out.getvalue()
            assert "'block_number': 3" in out.getvalue()
        mock_method.assert_called_once()

    def test_get_blocks_when_blocks_are_missed(self, file_blockchain_with_three_block_chunks):
        with patch.object(
            BlockchainBase, 'get_instance', return_value=file_blockchain_with_three_block_chunks
        ) as mock_method:
            out = StringIO()
            self.run_command('get-blocks', 10, 11, stdout=out)
            assert out.getvalue() == ''
        mock_method.assert_called_once()

    def test_get_blocks_when_start_and_end_block_are_equal(self, file_blockchain_with_three_block_chunks):
        with patch.object(
            BlockchainBase, 'get_instance', return_value=file_blockchain_with_three_block_chunks
        ) as mock_method:
            out = StringIO()
            self.run_command('get-blocks', 2, 2, stdout=out)
            assert "'block_number\': 2" in out.getvalue()
        mock_method.assert_called_once()

    def test_get_blocks_when_start_number_is_high_than_end_number(self, file_blockchain_with_three_block_chunks):
        with patch.object(
            BlockchainBase, 'get_instance', return_value=file_blockchain_with_three_block_chunks
        ) as mock_method:
            out = StringIO()
            self.run_command('get-blocks', 3, 2, stdout=out)
            assert 'End block argument should be equal or more than start block.' in out.getvalue()
        mock_method.assert_called_once()

    def test_get_blockchain_state(self, file_blockchain_with_three_block_chunks):
        with patch.object(
            BlockchainBase, 'get_instance', return_value=file_blockchain_with_three_block_chunks
        ) as mock_method:
            out = StringIO()
            self.run_command('get-blockchain-state', 2, stdout=out)
            assert "{'message': {'account_states'" in out.getvalue()
        mock_method.assert_called_once()
