import logging
import random

from tqdm import tqdm

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.models import CoinTransferSignedChangeRequest
from thenewboston_node.business_logic.models.node import RegularNode
from thenewboston_node.business_logic.utils.blockchain_state import make_blockchain_genesis_state
from thenewboston_node.core.utils.cryptography import generate_key_pair

MAX_AMOUNT = 100

logger = logging.getLogger(__name__)


def pick_recipient(candidates, exclude=(), pick_existing_probability=0.5):
    recipient = None
    private_key = None
    if random.random() < pick_existing_probability:
        recipient = random.choice(candidates)
        if recipient in exclude:
            recipient = None

    if recipient is None:
        recipient_key_pair = generate_key_pair()
        logger.info('New recipient account: %s', recipient_key_pair)
        recipient = recipient_key_pair.public
        private_key = recipient_key_pair.private

    return recipient, private_key


def get_initial_balances(blockchain):
    return {
        account: balance.balance for account, balance in blockchain.get_first_blockchain_state().account_states.items()
    }


def generate_blockchain(
    blockchain: BlockchainBase,
    size,
    signing_key,
    add_blockchain_genesis_state=True,
    validate=True,
    treasury_account_key_pair=None
):
    treasury_account_key_pair = treasury_account_key_pair or generate_key_pair()
    treasury_account = treasury_account_key_pair.public
    logger.info('Using treasury account: %s', treasury_account_key_pair)

    if add_blockchain_genesis_state and blockchain.get_blockchain_states_count() == 0:
        blockchain_genesis_state = make_blockchain_genesis_state(
            treasury_account_number=treasury_account, primary_validator_schedule_end_block_number=size + 99
        )
        blockchain.add_blockchain_state(blockchain_genesis_state)

    primary_validator = blockchain.get_primary_validator()
    assert primary_validator
    pv_fee = primary_validator.fee_amount

    preferred_node = RegularNode(identifier=generate_key_pair().public, fee_amount=1, network_addresses=[])
    node_fee = preferred_node.fee_amount

    balances = get_initial_balances(blockchain)

    assert len(balances) >= 1
    assert treasury_account in balances
    assert balances[treasury_account] >= MAX_AMOUNT
    balances = {treasury_account: balances[treasury_account]}
    accounts = list(balances)

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

        signed_change_request = CoinTransferSignedChangeRequest.from_main_transaction(
            blockchain=blockchain,
            recipient=recipient,
            amount=amount,
            signing_key=sender_private_key,
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
        pv = blockchain.get_primary_validator()
        assert pv

        blockchain.add_block_from_signed_change_request(signed_change_request, signing_key, validate=validate)


def get_attribute_default_value(attribute, account):
    if attribute == 'balance':
        return 0
    elif attribute == 'balance_lock':
        return account

    return None
