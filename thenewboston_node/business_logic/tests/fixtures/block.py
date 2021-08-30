import pytest

from thenewboston_node.business_logic import models


@pytest.fixture
def block_0(
    blockchain_base, treasury_account_key_pair, primary_validator_key_pair, user_account, preferred_node
) -> models.Block:
    return models.Block.create_from_main_transaction(
        blockchain=blockchain_base,
        recipient=user_account,
        amount=99,
        request_signing_key=treasury_account_key_pair.private,
        pv_signing_key=primary_validator_key_pair.private,
        preferred_node=preferred_node,
    )


@pytest.fixture
def block_1(
    blockchain_base, treasury_account_key_pair, primary_validator_key_pair, user_account, preferred_node
) -> models.Block:
    block = models.Block.create_from_main_transaction(
        blockchain=blockchain_base,
        recipient=user_account,
        amount=199,
        request_signing_key=treasury_account_key_pair.private,
        pv_signing_key=primary_validator_key_pair.private,
        preferred_node=preferred_node,
    )
    block.message.block_number = 1
    return block


@pytest.fixture
def block_2(
    blockchain_base, treasury_account_key_pair, primary_validator_key_pair, user_account, preferred_node
) -> models.Block:
    block = models.Block.create_from_main_transaction(
        blockchain=blockchain_base,
        recipient=user_account,
        amount=299,
        request_signing_key=treasury_account_key_pair.private,
        pv_signing_key=primary_validator_key_pair.private,
        preferred_node=preferred_node,
    )
    block.message.block_number = 2
    return block
