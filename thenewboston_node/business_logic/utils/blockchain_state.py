import json
import logging
from contextlib import closing
from typing import Optional, cast
from urllib.request import urlopen

from django.conf import settings

from thenewboston_node.business_logic.models import (
    AccountState, BlockchainState, BlockchainStateMessage, PrimaryValidator
)
from thenewboston_node.business_logic.models.signed_change_request_message.pv_schedule import PrimaryValidatorSchedule
from thenewboston_node.business_logic.node import get_node_identifier
from thenewboston_node.business_logic.storages.file_system import read_compressed_file
from thenewboston_node.business_logic.utils.network import make_own_node
from thenewboston_node.core.utils.cryptography import derive_public_key
from thenewboston_node.core.utils.misc import is_valid_url

logger = logging.getLogger()


# TODO(dmu) MEDIU: Refactor `read_account_root_file_source` and `read_blockchain_state_file_from_source` to something
#                  similar to `BinaryDataBlockSource`
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


# TODO(dmu) HIGH: Migrate to `BlockchainStateBuilder`
def make_blockchain_genesis_state(
    *,
    treasury_account_number,
    treasury_account_initial_balance=281474976710656,
    primary_validator=None,
    primary_validator_identifier=None,
    primary_validator_network_addresses=('http://localhost:8555/',),
    primary_validator_fee_amount=4,
    primary_validator_fee_account=None,
    primary_validator_schedule_begin_block_number=0,
    primary_validator_schedule_end_block_number=99,
    primary_validator_signing_key=None,
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
    blockchain_state = BlockchainState(
        message=BlockchainStateMessage(account_states=accounts), signer=primary_validator.identifier
    )
    if primary_validator_signing_key:
        blockchain_state.sign(signing_key=primary_validator_signing_key)

    return blockchain_state


class BlockchainStateBuilder:

    def __init__(self):
        self.treasury_account_number = None
        self.treasury_account_initial_balance = None

        self.primary_validator = None
        self.pv_schedule_begin_block_number = None
        self.pv_schedule_end_block_number = None

        self.confirmation_validator = None
        self.cv_schedule_begin_block_number = None
        self.cv_schedule_end_block_number = None

        self.signing_key = None

    def set_treasury_account(self, account_number, balance=281474976710656):
        self.treasury_account_number = account_number
        self.treasury_account_initial_balance = balance

    def set_primary_validator(self, primary_validator, schedule_begin_block_number, schedule_end_block_number):
        self.primary_validator = primary_validator
        self.pv_schedule_begin_block_number = schedule_begin_block_number
        self.pv_schedule_end_block_number = schedule_end_block_number

    def set_blockchain_state_signing_key(self, signing_key):
        self.signing_key = signing_key

    def set_confirmation_validator(
        self, confirmation_validator, schedule_begin_block_number, schedule_end_block_number
    ):
        self.confirmation_validator = confirmation_validator
        self.cv_schedule_begin_block_number = schedule_begin_block_number
        self.cv_schedule_end_block_number = schedule_end_block_number

    def get_blockchain_state(self) -> BlockchainState:
        accounts = {}

        treasury_account_number = self.treasury_account_number
        if treasury_account_number:
            treasury_account_initial_balance = self.treasury_account_initial_balance
            assert treasury_account_initial_balance is not None
            accounts[treasury_account_number] = AccountState(balance=treasury_account_initial_balance)

        primary_validator = self.primary_validator
        if primary_validator:
            schedule_begin_block_number = self.pv_schedule_begin_block_number
            schedule_end_block_number = self.pv_schedule_end_block_number
            assert schedule_begin_block_number is not None
            assert schedule_end_block_number is not None

            accounts[primary_validator.identifier] = AccountState(
                node=primary_validator,
                primary_validator_schedule=PrimaryValidatorSchedule(
                    begin_block_number=schedule_begin_block_number,
                    end_block_number=schedule_end_block_number,
                )
            )

        confirmation_validator = self.confirmation_validator
        if confirmation_validator:
            schedule_begin_block_number = self.cv_schedule_begin_block_number
            schedule_end_block_number = self.cv_schedule_end_block_number
            assert schedule_begin_block_number is not None
            assert schedule_end_block_number is not None

            accounts[confirmation_validator.identifier] = AccountState(
                node=confirmation_validator,
                primary_validator_schedule=PrimaryValidatorSchedule(
                    begin_block_number=schedule_begin_block_number,
                    end_block_number=schedule_end_block_number,
                )
            )

        signing_key = self.signing_key
        signer = None if signing_key is None else derive_public_key(signing_key)
        blockchain_state = BlockchainState(message=BlockchainStateMessage(account_states=accounts), signer=signer)
        if signing_key:
            blockchain_state.sign(signing_key=signing_key)

        return blockchain_state
