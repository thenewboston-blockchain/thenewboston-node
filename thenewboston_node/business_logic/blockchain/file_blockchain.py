import logging
import os.path
from typing import Generator

import msgpack

from thenewboston_node.business_logic.models.account_root_file import AccountRootFile
from thenewboston_node.business_logic.models.block import Block
from thenewboston_node.business_logic.storages.file_system import FileSystemStorage

from .base import BlockchainBase

logger = logging.getLogger(__name__)

ORDER_OF_ACCOUNT_ROOT_FILE = 10


class FileBlockchain(BlockchainBase):

    def __init__(self, base_directory, validate=True):
        if not os.path.isabs(base_directory):
            raise ValueError('base_directory must be an absolute path')

        self.account_root_files_directory = os.path.join(base_directory, 'account-root-files')
        self.blocks_directory = os.path.join(base_directory, 'blocks')
        self.base_directory = base_directory

        self.storage = FileSystemStorage()

        if validate:
            self.validate()

    def iter_blocks(self) -> Generator[Block, None, None]:
        storage = self.storage
        for file_path in storage.list_directory(self.blocks_directory):
            assert file_path
            yield NotImplemented

    def iter_account_root_files(self) -> Generator[AccountRootFile, None, None]:
        storage = self.storage
        for file_path in storage.list_directory(self.account_root_files_directory):
            yield AccountRootFile.from_compact_dict(msgpack.unpackb(storage.load(file_path)))

    def add_account_root_file(self, account_root_file: AccountRootFile):
        last_block_number = account_root_file.last_block_number

        prefix = ('.' if last_block_number is None else str(last_block_number)).zfill(ORDER_OF_ACCOUNT_ROOT_FILE)
        file_path = os.path.join(self.account_root_files_directory, f'{prefix}-arf.msgpack')
        self.storage.save(file_path, msgpack.packb(account_root_file.to_compact_dict()), is_final=True)
