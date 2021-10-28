import pytest

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.business_logic.models import Block, CoinTransferSignedChangeRequest


def test_transfer_to_itself_is_not_validated(
    file_blockchain, treasury_account_key_pair, preferred_node, primary_validator_key_pair
):
    treasury_account = treasury_account_key_pair.public
    request = CoinTransferSignedChangeRequest.create_from_main_transaction(
        blockchain=file_blockchain,
        recipient=treasury_account,
        amount=99,
        signing_key=treasury_account_key_pair.private,
        node=preferred_node
    )
    block = Block.create_from_signed_change_request(file_blockchain, request, primary_validator_key_pair.private)

    with pytest.raises(ValidationError, match=f'Cannot transfer coins from account {treasury_account} to itself'):
        file_blockchain.add_block(block)
