#!/usr/bin/env python3
import builtins
import datetime
import os
import sys
import textwrap
import typing
from inspect import getdoc
from typing import get_type_hints

import django

import class_doc
import jinja2

from thenewboston_node.business_logic import models
from thenewboston_node.business_logic.blockchain import file_blockchain
from thenewboston_node.business_logic.models.base import BlockType
from thenewboston_node.business_logic.models.mixins.compactable import COMPACT_KEY_MAP
from thenewboston_node.business_logic.storages import file_system, path_optimized_file_system
from thenewboston_node.core.utils.dataclass import is_optional

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath('../..')

TEMPLATE_PATH = 'index.rst'

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

TYPE_NAME_MAP = {
    'str': 'string',
    'int': 'integer',
    'dict': 'object',
    'list': 'array',
    'tuple': 'array',
}

BLOCK_SAMPLE = models.Block(
    signer='4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732',
    message_hash='9677f4cbd7aaf32ba9615416f7bd0991b7de1434a7fa2c31add25c3355ef3959',
    signature='d1c49087103b631a58228bdf8fb70d4789259cf22d815e207660cfe8d478ad'
    'ad9c7affe587942203e08be1dc1e14c6dd5a8abd8640f328e45f667a91a7c06a06',
    message=models.BlockMessage(
        block_type=BlockType.COIN_TRANSFER.value,
        block_identifier='d606af9d1d769192813d71051148ef1896e3d85062c31ad3e62331e25d9c96bc',
        block_number=0,
        timestamp=datetime.datetime(2021, 1, 1),
        signed_change_request=models.CoinTransferSignedChangeRequest(
            message=models.CoinTransferSignedChangeRequestMessage(
                balance_lock='cb0467e380e032881e3f5c26878da3584f1dc1f2262ef77ba5e1fa7ef4b2821c',
                txs=[
                    models.CoinTransferTransaction(
                        amount=54,
                        recipient='8d3bf5323afa7a8c6bc9418288e96491a0434a98925bf392835bfdb5a4f817ff',
                    ),
                    models.CoinTransferTransaction(
                        amount=5,
                        recipient='4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732',
                        fee=True,
                    ),
                    models.CoinTransferTransaction(
                        amount=1,
                        recipient='1be4f03ab7ea1184dbb5e4ff53b8cf0fe1cc400150ca1476fcd10546c1b3cd6a',
                        fee=True,
                    )
                ]
            ),
            signature='ae74562897f228a3d9bc388eba5037f34393e33813086c103bb5d6fc39a0'
            '23408655057f4ed8593c2d36bc98fb468112fdac186bec616ec2f2ba45c579c02108',
            signer='cb0467e380e032881e3f5c26878da3584f1dc1f2262ef77ba5e1fa7ef4b2821c',
        ),
        updated_account_states={
            '1be4f03ab7ea1184dbb5e4ff53b8cf0fe1cc400150ca1476fcd10546c1b3cd6a': models.AccountState(balance=1),
            '4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732': models.AccountState(balance=4),
            '8d3bf5323afa7a8c6bc9418288e96491a0434a98925bf392835bfdb5a4f817ff': models.AccountState(balance=54),
        },
    ),
)

BLOCKCHAIN_STATE_SAMPLE = models.BlockchainState(
    account_states={
        '1be4f03ab7ea1184dbb5e4ff53b8cf0fe1cc400150ca1476fcd10546c1b3cd6a':
            models.AccountState(
                balance=1,
                balance_lock='1be4f03ab7ea1184dbb5e4ff53b8cf0fe1cc400150ca1476fcd10546c1b3cd6a',
            ),
        '4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732':
            models.AccountState(
                balance=4,
                balance_lock='4d3cf1d9e4547d324de2084b568f807ef12045075a7a01b8bec1e7f013fc3732',
            ),
        '8d3bf5323afa7a8c6bc9418288e96491a0434a98925bf392835bfdb5a4f817ff':
            models.AccountState(
                balance=54,
                balance_lock='8d3bf5323afa7a8c6bc9418288e96491a0434a98925bf392835bfdb5a4f817ff',
            ),
    },
    last_block_number=100,
    last_block_identifier='d606af9d1d769192813d71051148ef1896e3d85062c31ad3e62331e25d9c96bc',
    last_block_timestamp=datetime.datetime(2021, 1, 1),
    next_block_identifier='18266e8fb5fba0ca9a0078d799c73ca34512c229519b1d021b8c2b78ef5f70b7',
)


def get_model_docs(model_classes):
    for model_class in model_classes:
        yield {
            'model': model_class.__name__,
            'docstring': getdoc(model_class),
            'attrs': list(get_model_attr_docs(model_class))
        }


def get_model_attr_docs(model):
    type_hints = get_type_hints(model)

    attribute_docs = extract_attribute_docs(model)
    for attr_name, attr_docstrings in attribute_docs.items():
        type_ = type_hints.get(attr_name)
        yield {
            'name': attr_name,
            'docstring': textwrap.dedent(attr_docstrings[0]),
            'type': get_type_representation(type_),
            'is_optional': is_optional(type_),
        }


def extract_attribute_docs(model):
    docs = {}
    for class_ in reversed(model.mro()):
        if class_ is not object:
            docs |= class_doc.extract_docs_from_cls_obj(cls=class_)

    return docs


def get_type_representation(type_):
    type_origin = typing.get_origin(type_)
    if type_origin in (dict, list, tuple):
        type_ = type_origin
    elif type_origin is typing.Union:
        type_args = list(typing.get_args(type_))
        try:
            type_args.remove(type(None))
        except ValueError:
            pass
        if len(type_args) == 1:
            type_ = type_args[0]

    try:
        type_str = type_.__name__
    except AttributeError:
        return ''
    return TYPE_NAME_MAP.get(type_str, type_str)


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
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(BASE_PATH))
    template = env.get_template(TEMPLATE_PATH)
    return template.render(context)


def setup():
    sys.path.insert(0, PROJECT_ROOT)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thenewboston_node.project.settings')
    django.setup()


def main():
    setup()
    rendered = render(get_context())
    print(rendered)


if __name__ == '__main__':
    main()
