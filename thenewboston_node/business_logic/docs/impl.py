import builtins

import jinja2

import thenewboston_node.business_logic.docs
from thenewboston_node.business_logic import models
from thenewboston_node.business_logic.blockchain import file_blockchain
from thenewboston_node.business_logic.models.mixins.compactable import COMPACT_KEY_MAP
from thenewboston_node.business_logic.storages import file_system, path_optimized_file_system

from .funcs import get_model_docs
from .samples import BLOCK_SAMPLE, BLOCKCHAIN_STATE_SAMPLE  # noqa: I101

BLOCK_MODELS = (
    models.Block,
    models.BlockMessage,
    models.CoinTransferSignedChangeRequest,
    models.CoinTransferSignedChangeRequestMessage,
    models.CoinTransferTransaction,
)

BLOCKCHAIN_STATE_MODELS = (
    models.BlockchainState,
    models.AccountState,
)


def get_context():
    return {
        'models': {
            'block': {
                'sample': BLOCK_SAMPLE,
                'docs': get_model_docs(model_classes=BLOCK_MODELS),
            },
            'blockchain_state': {
                'sample': BLOCKCHAIN_STATE_SAMPLE,
                'docs': get_model_docs(model_classes=BLOCKCHAIN_STATE_MODELS),
            }
        },
        'file_blockchain': {
            'account_root_file_subdir': file_blockchain.DEFAULT_ACCOUNT_ROOT_FILE_SUBDIR,
            'blocks_subdir': file_blockchain.DEFAULT_BLOCKS_SUBDIR,
            'block_chunk_size': file_blockchain.DEFAULT_BLOCK_CHUNK_SIZE,
            'order_of_block': file_blockchain.ORDER_OF_BLOCK,
            'order_of_account_root_file': file_blockchain.ORDER_OF_ACCOUNT_ROOT_FILE,
            'block_chunk_template': file_blockchain.BLOCK_CHUNK_FILENAME_TEMPLATE,
            'account_root_file_template': file_blockchain.ACCOUNT_ROOT_FILE_FILENAME_TEMPLATE,
            'get_block_chunk_filename': file_blockchain.get_block_chunk_filename,
            'get_account_root_filename': file_blockchain.get_account_root_filename,
            'compressors': file_system.COMPRESSION_FUNCTIONS.keys(),
            'file_optimization_max_depth': path_optimized_file_system.DEFAULT_MAX_DEPTH,
            'make_optimized_file_path': path_optimized_file_system.make_optimized_file_path,
        },
        'compact_key_map': sorted(COMPACT_KEY_MAP.items()),
        'builtins': builtins,
    }


def render(context):
    env = jinja2.Environment(loader=jinja2.PackageLoader(thenewboston_node.business_logic.docs.__name__, 'templates'))
    template = env.get_template('blockchain_structure.rst')
    return template.render(context)


def main():
    rendered = render(get_context())
    print(rendered)
