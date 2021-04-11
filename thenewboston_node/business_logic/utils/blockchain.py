import random

from tqdm import tqdm

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.models.account_balance import AccountBalance
from thenewboston_node.business_logic.models.account_root_file import AccountRootFile
from thenewboston_node.business_logic.models.node import PrimaryValidator, RegularNode
from thenewboston_node.business_logic.models.transfer_request import TransferRequest
from thenewboston_node.business_logic.node import get_node_identifier
from thenewboston_node.core.utils.cryptography import generate_key_pair

MAX_AMOUNT = 100


def pick_recipient(candidates, exclude=(), pick_existing_probability=0.5):
    recipient = None
    private_key = None
    if random.random() < pick_existing_probability:
        recipient = random.choice(candidates)
        if recipient in exclude:
            recipient = None

    if recipient is None:
        recipient_key_pair = generate_key_pair()
        recipient = recipient_key_pair.public
        private_key = recipient_key_pair.private

    return recipient, private_key


def get_initial_balances(blockchain):
    return {account: balance.value for account, balance in blockchain.get_first_account_root_file().accounts.items()}


def generate_blockchain(
    blockchain: BlockchainBase,
    size,
    add_initial_account_root_file=True,
    validate=True,
    treasury_account_key_pair=None
):
    treasury_account_key_pair = treasury_account_key_pair or generate_key_pair()
    treasury_account = treasury_account_key_pair.public

    if add_initial_account_root_file and blockchain.get_account_root_file_count() == 0:
        initial_account_root_file = AccountRootFile(
            accounts={treasury_account: AccountBalance(value=281474976710656, lock=treasury_account)}
        )
        blockchain.add_account_root_file(initial_account_root_file)

    primary_validator = PrimaryValidator(identifier=get_node_identifier(), fee_amount=4)
    pv_fee = primary_validator.fee_amount

    preferred_node = RegularNode(identifier=generate_key_pair().public, fee_amount=1)
    node_fee = preferred_node.fee_amount

    balances = get_initial_balances(blockchain)
    accounts = list(balances)

    assert len(balances) == 1
    assert treasury_account in balances
    assert balances[treasury_account] >= MAX_AMOUNT

    account_private_keys = {treasury_account: treasury_account_key_pair.private}
    sender_candidates = {treasury_account}
    min_sender_amount = MAX_AMOUNT + pv_fee + node_fee

    for _ in tqdm(range(size)):
        amount = random.randint(1, MAX_AMOUNT)
        # TODO(dmu) MEDIUM: Improve performance at tuple(sender_candidates)
        sender = random.choice(tuple(sender_candidates))
        sender_private_key = account_private_keys[sender]

        recipient, recipient_private_key = pick_recipient(accounts, exclude=(sender,))
        if recipient_private_key:
            # We got new recipient
            accounts.append(recipient)
            account_private_keys[recipient] = recipient_private_key

        transfer_request = TransferRequest.from_main_transaction(
            blockchain=blockchain,
            recipient=recipient,
            amount=amount,
            signing_key=sender_private_key,
            primary_validator=primary_validator,
            node=preferred_node
        )

        sender_new_balance = balances[sender] - (amount + pv_fee + node_fee)
        balances[sender] = sender_new_balance
        if sender_new_balance < min_sender_amount:
            sender_candidates.discard(sender)

        recipient_new_balance = balances.get(recipient, 0) + amount
        balances[recipient] = recipient_new_balance
        if recipient_new_balance >= min_sender_amount:
            sender_candidates.add(recipient)

        blockchain.add_block_from_transfer_request(transfer_request, validate=validate)
