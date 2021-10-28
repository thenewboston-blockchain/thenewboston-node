import pytest

from thenewboston_node.business_logic import exceptions
from thenewboston_node.business_logic.models import Block, CoinTransferSignedChangeRequest


def test_cannot_create_signed_change_request_block_if_not_enough_balance_for_fees(
    file_blockchain, primary_validator_key_pair, treasury_account_key_pair, treasury_initial_balance, user_account,
    preferred_node, primary_validator
):
    treasury_account = treasury_account_key_pair.public
    transfer_amount = treasury_initial_balance - preferred_node.fee_amount - primary_validator.fee_amount + 1

    request = CoinTransferSignedChangeRequest.create_from_main_transaction(
        blockchain=file_blockchain,
        recipient=user_account,
        amount=transfer_amount,
        signing_key=treasury_account_key_pair.private,
        node=preferred_node
    )
    with pytest.raises(
        exceptions.CoinTransferRequestError,
        match=f"Sender's account {treasury_account} has not enough balance to send 281474976710657 coins"
    ):
        Block.create_from_signed_change_request(
            blockchain=file_blockchain,
            signed_change_request=request,
            pv_signing_key=primary_validator_key_pair.private
        )
