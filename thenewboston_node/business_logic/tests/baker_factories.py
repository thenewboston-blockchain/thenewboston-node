from typing import Any

from thenewboston_node.business_logic import models
from thenewboston_node.business_logic.models.signed_change_request import SIGNED_CHANGE_REQUEST_TYPE_MAP
from thenewboston_node.business_logic.models.signed_change_request.constants import BlockType
from thenewboston_node.core.utils import baker
from thenewboston_node.core.utils.baker import RandomNoTzDatetimeGenerator


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
    defaults = {'last_block_timestamp': {'_generator_': RandomNoTzDatetimeGenerator}}
    return baker.make(models.BlockchainStateMessage, _attr_defaults=defaults, **kwargs)


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
