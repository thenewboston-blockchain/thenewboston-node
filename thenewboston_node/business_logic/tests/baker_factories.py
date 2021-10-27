import random
from typing import Any

from dataclass_bakery.generators import defaults
from dataclass_bakery.generators.random_generator import RandomGenerator
from dataclass_bakery.generators.random_str_generator import RandomStrGenerator

from thenewboston_node.business_logic import models
from thenewboston_node.business_logic.models.constants import BlockType
from thenewboston_node.business_logic.models.signed_change_request import SIGNED_CHANGE_REQUEST_TYPE_MAP
from thenewboston_node.core.utils import baker
from thenewboston_node.core.utils.baker import RandomHexGenerator, RandomNoTzDatetimeGenerator


class AccountStatesGenerator(RandomGenerator):

    def generate(self, *args, **kwargs) -> dict[str, models.AccountState]:
        max_length = defaults.MAX_DICT_LENGTH
        account_no_generator = RandomHexGenerator()

        block_counter, block_increment = 0, 99
        account_states = {}
        for _ in range(max_length):
            account_number = account_no_generator.generate()
            account_state = make_account_state(
                primary_validator_schedule__begin_block_number=block_counter,
                primary_validator_schedule__end_block_number=block_counter + block_increment,
                node__identifier=account_number,
            )
            account_states[account_number] = account_state
            block_counter += block_increment + 1

        return account_states


class RandomNetworkAddressesGenerator(RandomGenerator):
    schemes = ('http', 'https')

    def generate(self, *args, **kwargs) -> list[str]:
        str_generator = RandomStrGenerator()
        max_length = defaults.MAX_DICT_LENGTH
        network_addresses = []
        for _ in range(max_length):
            scheme = random.choice(self.schemes)
            host = str_generator.generate().lower()
            port = random.randint(1, 0xffff)
            network_addresses.append(f'{scheme}://{host}.random:{port}')
        return network_addresses


def make_block(block_type, **kwargs):
    kwargs = _break_nested_kwargs(kwargs)
    message = make_block_message(block_type, **kwargs.pop('message', {}))

    return baker.make(models.Block, message=message, **kwargs)


def make_block_message(block_type, **kwargs):
    kwargs = _break_nested_kwargs(kwargs)
    signed_change_request = make_signed_change_request(block_type, **kwargs.pop('signed_change_request', {}))
    message = baker.make(
        models.BlockMessage, block_type=block_type, signed_change_request=signed_change_request, **kwargs
    )
    for account_number, account_state in message.updated_account_states.items():
        account_state.node.identifier = account_number
    return message


def make_signed_change_request(block_type, **kwargs):
    kwargs = _break_nested_kwargs(kwargs)
    request_class = SIGNED_CHANGE_REQUEST_TYPE_MAP.get(block_type)
    if not request_class:
        raise NotImplementedError(f'Block type {block_type} is not supported yet')

    return baker.make(request_class, **kwargs)


def make_coin_transfer_block(**kwargs):
    return make_block(block_type=BlockType.COIN_TRANSFER.value, **kwargs)


def make_node_declaration_block(**kwargs):
    return make_block(block_type=BlockType.NODE_DECLARATION.value, **kwargs)


def make_blockchain_state(**kwargs):
    kwargs = _break_nested_kwargs(kwargs)
    message = make_blockchain_state_message(**kwargs.pop('message', {}))
    return baker.make(models.BlockchainState, message=message, **kwargs)


def make_genesis_blockchain_state(**kwargs):
    return make_blockchain_state(
        message__last_block_number=None,
        message__last_block_identifier=None,
        message__last_block_timestamp=None,
        message__next_block_identifier=None,
        **kwargs
    )


def make_blockchain_state_message(**kwargs):
    kwargs = _break_nested_kwargs(kwargs)
    _attr_defaults = {
        'last_block_timestamp': {
            '_generator_': RandomNoTzDatetimeGenerator
        },
        'account_states': {
            '_generator_': AccountStatesGenerator
        },
    }
    return baker.make(models.BlockchainStateMessage, _attr_defaults=_attr_defaults, **kwargs)


def make_account_state(**kwargs):
    kwargs = _break_nested_kwargs(kwargs)
    node = make_node(**kwargs.pop('node', {}))
    primary_validator_schedule = make_primary_validator_schedule(**kwargs.pop('primary_validator_schedule', {}))
    return baker.make(models.AccountState, node=node, primary_validator_schedule=primary_validator_schedule, **kwargs)


def make_node(**kwargs):
    kwargs = _break_nested_kwargs(kwargs)
    _attr_defaults = {'network_addresses': {'_generator_': RandomNetworkAddressesGenerator}}
    return baker.make(models.Node, _attr_defaults=_attr_defaults, **kwargs)


def make_primary_validator_schedule(**kwargs):
    kwargs = _break_nested_kwargs(kwargs)
    kwargs.setdefault('begin_block_number', 0)
    kwargs.setdefault('end_block_number', 99)
    return baker.make(models.PrimaryValidatorSchedule, **kwargs)


def _break_nested_kwargs(kwargs: dict[str, Any]):
    new_kwargs = {}
    for key, value in kwargs.items():
        try:
            top_key, subkey = key.split('__', 1)
        except ValueError:
            new_kwargs[key] = value
            continue

        new_kwargs.setdefault(top_key, {})
        new_kwargs[top_key] |= {subkey: value}

    return new_kwargs
