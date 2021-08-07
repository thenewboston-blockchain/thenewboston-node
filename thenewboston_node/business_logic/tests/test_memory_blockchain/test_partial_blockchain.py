from datetime import datetime

from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain
from thenewboston_node.business_logic.models import CoinTransferSignedChangeRequest
from thenewboston_node.business_logic.models.account_state import AccountState
from thenewboston_node.business_logic.models.blockchain_state import BlockchainState
from thenewboston_node.business_logic.models.signed_change_request_message.pv_schedule import PrimaryValidatorSchedule
from thenewboston_node.business_logic.node import get_node_signing_key
from thenewboston_node.core.utils.cryptography import generate_key_pair


def test_partial_blockchain(primary_validator, preferred_node):
    account1_key_pair = generate_key_pair()
    account2_key_pair = generate_key_pair()
    account3_key_pair = generate_key_pair()
    new_account_key_pair = generate_key_pair()

    fake_lock1, _ = generate_key_pair()
    fake_lock2, _ = generate_key_pair()
    fake_lock3, _ = generate_key_pair()

    base_blockchain_state = BlockchainState(
        account_states={
            account1_key_pair.public:
                AccountState(balance=1000, balance_lock=fake_lock1),
            account2_key_pair.public:
                AccountState(balance=2000, balance_lock=fake_lock2),
            account3_key_pair.public:
                AccountState(balance=3000, balance_lock=fake_lock3),
            primary_validator.identifier:
                AccountState(
                    node=primary_validator,
                    primary_validator_schedule=PrimaryValidatorSchedule(begin_block_number=0, end_block_number=9999)
                ),
        },
        last_block_number=1234,
        last_block_identifier='23203d245b5e128465669223b5220b3061af1e2e72b0429ef26b07ce3a2282e7',
        last_block_timestamp=datetime.utcnow(),
        next_block_identifier='626dea61c1a6480d6a4c9cd657c7d7be52ddc38e5f2ec590b609ac01edde62fd',
    )

    blockchain = MemoryBlockchain()
    blockchain.add_blockchain_state(base_blockchain_state)
    primary_validator = blockchain.get_primary_validator()
    assert primary_validator

    assert blockchain.get_block_count() == 0
    assert blockchain.get_account_current_balance(account1_key_pair.public) == 1000
    assert blockchain.get_account_current_balance(account2_key_pair.public) == 2000
    assert blockchain.get_account_current_balance(account3_key_pair.public) == 3000
    assert blockchain.get_account_current_balance(new_account_key_pair.public) == 0
    blockchain.validate()

    signed_change_request1 = CoinTransferSignedChangeRequest.from_main_transaction(
        blockchain=blockchain,
        recipient=account2_key_pair.public,
        amount=10,
        signing_key=account1_key_pair.private,
        node=preferred_node
    )
    signed_change_request1.validate(blockchain, blockchain.get_next_block_number())
    blockchain.add_block_from_signed_change_request(signed_change_request1, get_node_signing_key())
    blockchain.validate()

    pv_fee = primary_validator.fee_amount
    node_fee = preferred_node.fee_amount
    assert pv_fee > 0
    assert node_fee > 0
    assert pv_fee != node_fee
    total_fees = pv_fee + node_fee

    assert blockchain.get_block_count() == 1
    assert blockchain.get_account_current_balance(account1_key_pair.public) == 1000 - 10 - total_fees
    assert blockchain.get_account_current_balance(account2_key_pair.public) == 2000 + 10
    assert blockchain.get_account_current_balance(account3_key_pair.public) == 3000
    assert blockchain.get_account_current_balance(new_account_key_pair.public) == 0

    signed_change_request2 = CoinTransferSignedChangeRequest.from_main_transaction(
        blockchain=blockchain,
        recipient=new_account_key_pair.public,
        amount=20,
        signing_key=account2_key_pair.private,
        node=preferred_node
    )
    signed_change_request2.validate(blockchain, blockchain.get_next_block_number())
    blockchain.add_block_from_signed_change_request(signed_change_request2, get_node_signing_key())
    blockchain.validate()

    assert blockchain.get_block_count() == 2
    assert blockchain.get_account_current_balance(account1_key_pair.public) == 1000 - 10 - total_fees
    assert blockchain.get_account_current_balance(account2_key_pair.public) == 2000 + 10 - 20 - total_fees
    assert blockchain.get_account_current_balance(account3_key_pair.public) == 3000
    assert blockchain.get_account_current_balance(new_account_key_pair.public) == 20

    blockchain.snapshot_blockchain_state()
    blockchain.validate()

    assert blockchain.get_account_current_balance(account1_key_pair.public) == 1000 - 10 - total_fees
    assert blockchain.get_account_current_balance(account2_key_pair.public) == 2000 + 10 - 20 - total_fees
    assert blockchain.get_account_current_balance(account3_key_pair.public) == 3000
    assert blockchain.get_account_current_balance(new_account_key_pair.public) == 20

    signed_change_request3 = CoinTransferSignedChangeRequest.from_main_transaction(
        blockchain=blockchain,
        recipient=account2_key_pair.public,
        amount=30,
        signing_key=account3_key_pair.private,
        node=preferred_node
    )
    signed_change_request3.validate(blockchain, blockchain.get_next_block_number())
    blockchain.add_block_from_signed_change_request(signed_change_request3, get_node_signing_key())
    blockchain.validate()

    assert blockchain.get_account_current_balance(account1_key_pair.public) == 1000 - 10 - total_fees
    assert blockchain.get_account_current_balance(account2_key_pair.public) == 2000 + 10 - 20 - total_fees + 30
    assert blockchain.get_account_current_balance(account3_key_pair.public) == 3000 - 30 - total_fees
    assert blockchain.get_account_current_balance(new_account_key_pair.public) == 20
