import builtins
from collections import Counter
from contextlib import closing

import jinja2

import thenewboston_node.business_logic.blockchain.file_blockchain.block_chunk
import thenewboston_node.business_logic.blockchain.file_blockchain.blockchain_state
import thenewboston_node.business_logic.docs
from thenewboston_node.business_logic import models
from thenewboston_node.business_logic.models import SignedChangeRequestMessage
from thenewboston_node.business_logic.models.mixins.compactable import COMPACT_KEY_MAP
from thenewboston_node.business_logic.models.signed_change_request import SIGNED_CHANGE_REQUEST_TYPE_MAP
from thenewboston_node.business_logic.models.signed_change_request.constants import BlockType
from thenewboston_node.business_logic.storages import file_system, path_optimized_file_system
from thenewboston_node.core.utils.misc import humanize_snake_case

from .samples import SamplesFactory  # noqa: I101


def get_block_models(exclude=()):
    block_models = models.Block.get_nested_models(include_self=True)
    return [model for model in block_models if model not in exclude]


def get_blockchain_state_models(exclude=()):
    blockchain_state_models = models.BlockchainState.get_nested_models(include_self=True)
    return [model for model in blockchain_state_models if model not in exclude]


def get_signed_change_request_message_child_models():
    return [
        signed_change_request_child_model.get_field_type('message')
        for _, signed_change_request_child_model in SIGNED_CHANGE_REQUEST_TYPE_MAP.items()
    ]


def get_signed_change_request_message_models(exclude=()):
    signed_change_request_message_child_models = get_signed_change_request_message_child_models()
    signed_change_request_message_models = []
    for model in signed_change_request_message_child_models:
        for nested_model in model.get_nested_models(include_self=True):
            if nested_model in exclude:
                continue

            signed_change_request_message_models.append(nested_model)

    return signed_change_request_message_models


def get_common_models():
    models = get_block_models() + get_signed_change_request_message_models() + get_blockchain_state_models()
    return [model for model, count in Counter(models).items() if count > 1]


def get_context(samples_factory):
    # TODO(dmu) MEDIUM: Is there a way to avoid duplicate traversable that does not hurt code readability?
    common_models = get_common_models()

    exclude = set(common_models) | {models.SignedChangeRequestMessage}

    block_models = get_block_models(exclude=exclude)
    blockchain_state_models = get_blockchain_state_models(exclude=exclude)
    signed_change_request_message_models = get_signed_change_request_message_models(exclude=exclude)

    # we need it a list to keep the same order with `signed_change_request_message_subtypes`
    assert isinstance(signed_change_request_message_models, list)
    signed_change_request_message_subtypes = [
        type_ for type_ in signed_change_request_message_models if issubclass(type_, SignedChangeRequestMessage)
    ]

    return {
        'models': {
            'block': block_models,
            'blockchain_state': blockchain_state_models,
            'common': common_models,
            'signed_change_request_message': signed_change_request_message_models,
            'signed_change_request_message_subtypes': signed_change_request_message_subtypes,
        },
        'sample_block_map': samples_factory.get_sample_block_map(),
        'sample_blockchain_state': samples_factory.get_sample_blockchain_state(),
        'block_types': {item.value: humanize_snake_case(item.name.lower()) for item in BlockType},
        'sample_file_blockchain': samples_factory.get_sample_blockchain(),
        'file_blockchain': {
            'order_of_block':
                thenewboston_node.business_logic.blockchain.file_blockchain.block_chunk.ORDER_OF_BLOCK,
            'order_of_account_root_file':
                thenewboston_node.business_logic.blockchain.file_blockchain.blockchain_state.
                ORDER_OF_BLOCKCHAIN_STATE_FILE,
            'block_chunk_template':
                thenewboston_node.business_logic.blockchain.file_blockchain.block_chunk.BLOCK_CHUNK_FILENAME_TEMPLATE,
            'account_root_file_template':
                thenewboston_node.business_logic.blockchain.file_blockchain.blockchain_state.
                BLOCKCHAIN_STATE_FILENAME_TEMPLATE,
            'get_block_chunk_filename':
                thenewboston_node.business_logic.blockchain.file_blockchain.block_chunk.make_block_chunk_filename,
            'get_account_root_filename':
                thenewboston_node.business_logic.blockchain.file_blockchain.blockchain_state.
                make_blockchain_state_filename,
            'compressors':
                file_system.COMPRESSION_FUNCTIONS.keys(),
            'file_optimization_max_depth':
                path_optimized_file_system.DEFAULT_MAX_DEPTH,
            'make_optimized_file_path':
                path_optimized_file_system.make_optimized_file_path,
        },
        'compact_key_map': sorted(COMPACT_KEY_MAP.items()),
        'builtins': builtins,
    }


def render(context):
    env = jinja2.Environment(loader=jinja2.PackageLoader(thenewboston_node.business_logic.docs.__name__, 'templates'))
    template = env.get_template('blockchain-format.rst')
    return template.render(context)


def main():
    with closing(SamplesFactory()) as samples_factory:
        rendered = render(get_context(samples_factory))

    print(rendered)
