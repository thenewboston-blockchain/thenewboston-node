import pytest

from thenewboston_node.business_logic.models import BlockMessage, CoinTransferSignedChangeRequest


@pytest.fixture
def block_message(memory_blockchain, user_account, treasury_account_signing_key, preferred_node, primary_validator):
    coin_transfer_signed_request = CoinTransferSignedChangeRequest.from_main_transaction(
        blockchain=memory_blockchain,
        recipient=user_account,
        amount=10,
        signing_key=treasury_account_signing_key,
        primary_validator=primary_validator,
        node=preferred_node,
    )
    block_message = BlockMessage.from_signed_change_request(memory_blockchain, coin_transfer_signed_request)
    yield block_message
