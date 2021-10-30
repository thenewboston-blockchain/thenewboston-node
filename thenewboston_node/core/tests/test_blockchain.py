from io import StringIO

from thenewboston_node.business_logic.tests.base import force_blockchain


def test_get_block(blockchain_management_command, file_blockchain_with_three_block_chunks):
    out = StringIO()
    with force_blockchain(file_blockchain_with_three_block_chunks):
        blockchain_management_command('get-block', 2, stdout=out)

    assert '"block_number": 2' in out.getvalue()


def test_get_block_when_block_is_missed(blockchain_management_command, file_blockchain_with_three_block_chunks):
    out = StringIO()
    with force_blockchain(file_blockchain_with_three_block_chunks):
        blockchain_management_command('get-block', 10, stdout=out)
    assert out.getvalue() == 'Block number 10 was not found in the blockchain\n'


def test_get_blocks(blockchain_management_command, file_blockchain_with_three_block_chunks):
    out = StringIO()
    with force_blockchain(file_blockchain_with_three_block_chunks):
        blockchain_management_command('get-blocks', 2, 3, stdout=out)

    out_value = out.getvalue()
    assert '"block_number": 2' in out_value
    assert '"block_number": 3' in out_value


def test_get_blocks_when_blocks_are_missed(blockchain_management_command, file_blockchain_with_three_block_chunks):
    out = StringIO()
    with force_blockchain(file_blockchain_with_three_block_chunks):
        blockchain_management_command('get-blocks', 10, 11, stdout=out)
    assert out.getvalue() == ''


def test_get_blocks_when_start_and_end_block_are_equal(
    blockchain_management_command, file_blockchain_with_three_block_chunks
):
    out = StringIO()
    with force_blockchain(file_blockchain_with_three_block_chunks):
        blockchain_management_command('get-blocks', 2, 2, stdout=out)
    assert '"block_number": 2' in out.getvalue()


def test_get_blockchain_state(blockchain_management_command, file_blockchain_with_three_block_chunks):
    out = StringIO()
    with force_blockchain(file_blockchain_with_three_block_chunks):
        blockchain_management_command('get-blockchain-state', '--block-number', 2, stdout=out)
    assert '{\n    "message": {\n        "account_states":' in out.getvalue()
