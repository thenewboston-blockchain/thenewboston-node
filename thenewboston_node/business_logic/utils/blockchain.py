import logging
import os
import random
import shutil
import time

from tqdm import tqdm

from thenewboston_node.business_logic.blockchain.base import BlockchainBase
from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
from thenewboston_node.business_logic.models import CoinTransferSignedChangeRequest, Node
from thenewboston_node.business_logic.models.node import RegularNode
from thenewboston_node.business_logic.node import get_node_identifier
from thenewboston_node.business_logic.utils.blockchain_state import BlockchainStateBuilder
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
        account: account_state.balance
        for account, account_state in blockchain.get_first_blockchain_state().yield_account_states()
    }


def generate_blockchain(
    blockchain: BlockchainBase,
    size,
    signing_key,
    add_blockchain_genesis_state=True,
    validate=True,
    treasury_account_key_pair=None,
    primary_validator_network_addresses=None,
    primary_validator_identifier=None,
):
    treasury_account_key_pair = treasury_account_key_pair or generate_key_pair()
    treasury_account = treasury_account_key_pair.public
    logger.info('Using treasury account: %s', treasury_account_key_pair)

    if add_blockchain_genesis_state and blockchain.get_blockchain_state_count() == 0:
        builder = BlockchainStateBuilder()
        builder.set_treasury_account(treasury_account, balance=281474976710656)
        builder.set_primary_validator(
            Node(
                identifier=primary_validator_identifier or get_node_identifier(),
                network_addresses=primary_validator_network_addresses or ['http://localhost:8555/'],
                fee_amount=4,
            ), 0, size + 99
        )

        blockchain_genesis_state = builder.get_blockchain_state()
        blockchain.add_blockchain_state(blockchain_genesis_state)

    primary_validator = blockchain.get_primary_validator()
    assert primary_validator
    pv_fee = primary_validator.fee_amount

    preferred_node = RegularNode(identifier=generate_key_pair().public, fee_amount=1, network_addresses=[])
    node_fee = preferred_node.fee_amount

    initial_balances = get_initial_balances(blockchain)

    assert treasury_account in initial_balances
    assert initial_balances[treasury_account] >= MAX_AMOUNT
    balances = {treasury_account: initial_balances[treasury_account]}
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


def sync_minimal(source_blockchain: BlockchainBase, target_blockchain: BlockchainBase):
    """
    Make `target_blockchain` contain `source_blockchain` last blockchain state and all blocks after it.
    Do it in optimized way, so if `target_blockchain` already contains the last blockchain state and / or some / all
    blocks after it then copy only missing data.
    """
    # TODO(dmu) CRITICAL: Take about blockchain forks: if blockchain states are on the same block number,
    #                    but the blockchain states actually differ with their content

    source_bs_last_block_number = source_blockchain.get_last_blockchain_state_last_block_number()
    target_bs_last_block_number = target_blockchain.get_last_blockchain_state_last_block_number()
    logger.debug(
        'Blockchain state last block numbers (source: %s, target: %s)', source_bs_last_block_number,
        target_bs_last_block_number
    )
    if source_bs_last_block_number > target_bs_last_block_number:
        # Source blockchain contains a more recent blockchain state. For simplicity we just clear target blockchain
        # entirely to replace with source blockchain data.

        # TODO(dmu) HIGH: Do not just clear target blockchain because we might need the entire blockchain and
        #                 just fill the gaps later

        source_blockchain_state = source_blockchain.get_last_blockchain_state()
        # TODO(dmu) MEDIUM: Take care about situation where blockchain is cleared, but source blockchain
        #                     could not be added because of an error
        #                     (make it transactional - do not leave blockchain broken)
        target_blockchain.clear()
        target_blockchain.add_blockchain_state(source_blockchain_state)

        from_block_number = target_blockchain.get_last_blockchain_state_last_block_number() + 1
    else:
        from_block_number = target_blockchain.get_last_block_number() + 1

    source_last_block_number = source_blockchain.get_last_block_number()
    logger.debug('Source blockchain last block number: %s', source_last_block_number)
    if source_last_block_number < from_block_number:
        return  # the target blockchain already contains all blocks after last blockchain state of source blockchain

    # Just add each block one-by-one to target blockchain
    logger.debug('Syncing blocks from %s to %s', from_block_number, source_last_block_number)
    for block in source_blockchain.yield_blocks_slice(from_block_number, source_last_block_number):
        logger.debug('Adding block %s', block.get_block_number())
        target_blockchain.add_block(block)


def sync_minimal_to_file_blockchain(source: BlockchainBase, target: FileBlockchain):
    """
    Sync minimal to file blockchain in transactional manner (so a file blockchain is never corrupted)
    """
    target_base_directory = target.get_base_directory()

    temporary_file_blockchain_directory = '{}.{}'.format(target_base_directory, int(time.time() * 100000))
    temporary_file_blockchain = FileBlockchain(base_directory=temporary_file_blockchain_directory)
    temporary_file_blockchain.copy_from(target)

    sync_minimal(source, temporary_file_blockchain)
    throw_away_blockchain_directory = '{}.{}'.format(temporary_file_blockchain_directory, int(time.time() * 100000))

    # Trying make the replacement as atomic as possible
    os.rename(target_base_directory, throw_away_blockchain_directory)
    try:
        os.rename(temporary_file_blockchain_directory, target_base_directory)
    except:  # noqa: E722, B001
        os.rename(throw_away_blockchain_directory, target_base_directory)
        raise

    shutil.rmtree(throw_away_blockchain_directory)
