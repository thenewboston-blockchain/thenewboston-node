import argparse
import os
import os.path
import sys

import django

from thenewboston_node.business_logic.blockchain.file_blockchain import FileBlockchain
from thenewboston_node.business_logic.blockchain.memory_blockchain import MemoryBlockchain
from thenewboston_node.business_logic.utils.blockchain import generate_blockchain


def main(size, path=None, validate=True):
    if path:
        if os.path.exists(path):
            print(f'Path {path} already exists')
            return

        os.makedirs(path)
        blockchain = FileBlockchain(base_directory=os.path.abspath(path))
    else:
        blockchain = MemoryBlockchain()

    generate_blockchain(blockchain, size, validate=validate)


def get_args():
    parser = argparse.ArgumentParser(
        description='Generate blockchain of random transactions',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('size', type=int, help='Number of blocks to generate')
    parser.add_argument('--path', help='Blockchain base directory (if not specified then memory blockchain is used)')
    parser.add_argument('--do-not-validate', action='store_true')
    return parser.parse_args()


def entry():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thenewboston_node.project.settings')
    django.setup()

    args = get_args()
    main(args.size, path=args.path, validate=not args.do_not_validate)
    return 0


if __name__ == '__main__':
    sys.exit(entry())
