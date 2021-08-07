import json
import logging
from contextlib import closing
from typing import Optional, cast
from urllib.request import urlopen

from django.conf import settings

from thenewboston_node.business_logic.models import AccountState, BlockchainState, PrimaryValidator
from thenewboston_node.business_logic.models.signed_change_request_message.pv_schedule import PrimaryValidatorSchedule
from thenewboston_node.business_logic.node import get_node_identifier
from thenewboston_node.business_logic.storages.file_system import read_compressed_file
from thenewboston_node.business_logic.utils.network import make_own_node
from thenewboston_node.core.utils.misc import is_valid_url

logger = logging.getLogger()


def read_account_root_file_source(source):
    if is_valid_url(source):
        fo = urlopen(source)
    else:
        fo = open(source)

    with closing(fo) as fo:
        return json.load(fo)


def read_blockchain_state_file_from_source(source) -> Optional[BlockchainState]:
    kwargs = {}
    if is_valid_url(source):
        kwargs['open_function'] = urlopen

    data = read_compressed_file(source, **kwargs)
    if data is None:
        return None

    return BlockchainState.from_messagepack(cast(bytes, data))


def add_blockchain_state_from_account_root_file(blockchain, source):
    message = f'Reading account root file from {source}'
    logger.info(message)
    account_root_file = read_account_root_file_source(source)
    logger.info('DONE: %s', message)

    logger.info('Converting')
    blockchain_state = BlockchainState.create_from_account_root_file(account_root_file)
    logger.info('DONE: Converting')

    node = make_own_node()
    node_identifier = node.identifier
    logger.info('Injecting node (identifier: %s)', node_identifier)
    account_state = blockchain_state.get_account_state(node_identifier)
    if account_state is None:
        account_state = AccountState()
        blockchain_state.set_account_state(node_identifier, account_state)

    account_state.node = node
    account_state.primary_validator_schedule = PrimaryValidatorSchedule(
        begin_block_number=0, end_block_number=settings.SCHEDULE_DEFAULT_LENGTH_IN_BLOCKS - 1
    )
    logger.info('DONE: Injecting node')

    logger.info('Adding the blockchain state')
    blockchain.add_blockchain_state(blockchain_state)
    logger.info('DONE: Adding the blockchain state')


def add_blockchain_state_from_blockchain_state(blockchain, source):
    message = f'Reading blockchain state from {source}'
    logger.info(message)
    blockchain_state = read_blockchain_state_file_from_source(source)
    if blockchain_state is None:
        raise IOError(f'Could not read blockchain state from {source}')
    logger.info('DONE: %s', message)

    logger.info('Adding the blockchain state')
    blockchain.add_blockchain_state(blockchain_state)
    logger.info('DONE: Adding the blockchain state')


def sync_blockchain_state():
    # Get latest blockchain state from local blockchain
    # Get latest blockchain state from node
    # If blockchain state from node is more recent then download it and add to the blockchain
    raise NotImplementedError


def make_blockchain_genesis_state(
    *,
    treasury_account_number,
    primary_validator=None,
    primary_validator_identifier=None,
    primary_validator_network_addresses=('https://localhost:8555/',),
    primary_validator_fee_amount=4,
    primary_validator_fee_account=None,
    treasury_account_initial_balance=settings.DEFAULT_TREASURY_ACCOUNT_INITIAL_BALANCE,
    primary_validator_schedule_begin_block_number=0,
    primary_validator_schedule_end_block_number=99,
):
    if primary_validator is None:
        primary_validator = PrimaryValidator(
            identifier=primary_validator_identifier or get_node_identifier(),
            network_addresses=list(primary_validator_network_addresses),
            fee_amount=primary_validator_fee_amount,
            fee_account=primary_validator_fee_account,
        )

    primary_validator_identifier = primary_validator.identifier
    assert primary_validator_identifier != treasury_account_number

    accounts = {
        treasury_account_number:
            AccountState(balance=treasury_account_initial_balance),
        primary_validator_identifier:
            AccountState(
                node=primary_validator,
                primary_validator_schedule=PrimaryValidatorSchedule(
                    begin_block_number=primary_validator_schedule_begin_block_number,
                    end_block_number=primary_validator_schedule_end_block_number
                )
            ),
    }
    return BlockchainState(account_states=accounts)
