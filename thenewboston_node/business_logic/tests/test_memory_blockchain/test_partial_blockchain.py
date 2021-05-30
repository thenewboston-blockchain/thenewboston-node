from datetime import datetime

from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain
from thenewboston_node.business_logic.models import CoinTransferSignedRequest
from thenewboston_node.business_logic.models.account_root_file import AccountRootFile
from thenewboston_node.business_logic.models.account_state import AccountState
from thenewboston_node.core.utils.cryptography import generate_key_pair


def test_partial_blockchain(primary_validator, preferred_node):
    account1_key_pair = generate_key_pair()
    account2_key_pair = generate_key_pair()
    account3_key_pair = generate_key_pair()
    new_account_key_pair = generate_key_pair()

    fake_lock1, _ = generate_key_pair()
    fake_lock2, _ = generate_key_pair()
    fake_lock3, _ = generate_key_pair()

    base_account_root_file = AccountRootFile(
        account_states={
            account1_key_pair.public: AccountState(balance=1000, balance_lock=fake_lock1),
            account2_key_pair.public: AccountState(balance=2000, balance_lock=fake_lock2),
            account3_key_pair.public: AccountState(balance=3000, balance_lock=fake_lock3),
        },
        last_block_number=1234,
        last_block_identifier='23203d245b5e128465669223b5220b3061af1e2e72b0429ef26b07ce3a2282e7',
        last_block_timestamp=datetime.utcnow(),
        next_block_identifier='626dea61c1a6480d6a4c9cd657c7d7be52ddc38e5f2ec590b609ac01edde62fd',
    )

    blockchain = MemoryBlockchain(account_root_files=[base_account_root_file])
    assert blockchain.get_block_count() == 0
    assert blockchain.get_account_balance(account1_key_pair.public) == 1000
    assert blockchain.get_account_balance(account2_key_pair.public) == 2000
    assert blockchain.get_account_balance(account3_key_pair.public) == 3000
    assert blockchain.get_account_balance(new_account_key_pair.public) is None
    blockchain.validate()

    transfer_request1 = CoinTransferSignedRequest.from_main_transaction(
        blockchain=blockchain,
        recipient=account2_key_pair.public,
        amount=10,
        signing_key=account1_key_pair.private,
        primary_validator=primary_validator,
        node=preferred_node
    )
    transfer_request1.validate(blockchain)
    blockchain.add_block_from_transfer_request(transfer_request1)
    blockchain.validate()

    assert blockchain.get_block_count() == 1
    assert blockchain.get_account_balance(account1_key_pair.public) == 1000 - 10 - 4 - 1
    assert blockchain.get_account_balance(account2_key_pair.public) == 2000 + 10
    assert blockchain.get_account_balance(account3_key_pair.public) == 3000
    assert blockchain.get_account_balance(new_account_key_pair.public) is None

    transfer_request2 = CoinTransferSignedRequest.from_main_transaction(
        blockchain=blockchain,
        recipient=new_account_key_pair.public,
        amount=20,
        signing_key=account2_key_pair.private,
        primary_validator=primary_validator,
        node=preferred_node
    )
    transfer_request2.validate(blockchain)
    blockchain.add_block_from_transfer_request(transfer_request2)
    blockchain.validate()

    assert blockchain.get_block_count() == 2
    assert blockchain.get_account_balance(account1_key_pair.public) == 1000 - 10 - 4 - 1
    assert blockchain.get_account_balance(account2_key_pair.public) == 2000 + 10 - 20 - 4 - 1
    assert blockchain.get_account_balance(account3_key_pair.public) == 3000
    assert blockchain.get_account_balance(new_account_key_pair.public) == 20

    blockchain.make_account_root_file()
    blockchain.validate()

    assert blockchain.get_account_balance(account1_key_pair.public) == 1000 - 10 - 4 - 1
    assert blockchain.get_account_balance(account2_key_pair.public) == 2000 + 10 - 20 - 4 - 1
    assert blockchain.get_account_balance(account3_key_pair.public) == 3000
    assert blockchain.get_account_balance(new_account_key_pair.public) == 20

    transfer_request3 = CoinTransferSignedRequest.from_main_transaction(
        blockchain=blockchain,
        recipient=account2_key_pair.public,
        amount=30,
        signing_key=account3_key_pair.private,
        primary_validator=primary_validator,
        node=preferred_node
    )
    transfer_request3.validate(blockchain)
    blockchain.add_block_from_transfer_request(transfer_request3)
    blockchain.validate()

    assert blockchain.get_account_balance(account1_key_pair.public) == 1000 - 10 - 4 - 1
    assert blockchain.get_account_balance(account2_key_pair.public) == 2000 + 10 - 20 - 4 - 1 + 30
    assert blockchain.get_account_balance(account3_key_pair.public) == 3000 - 30 - 4 - 1
    assert blockchain.get_account_balance(new_account_key_pair.public) == 20
