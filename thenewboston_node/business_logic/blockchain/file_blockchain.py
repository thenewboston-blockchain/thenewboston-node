import logging
import os.path
from typing import Generator

from thenewboston_node.business_logic.models.account_root_file import AccountRootFile
from thenewboston_node.business_logic.storages.file_system import FileSystemStorage

from .base import BlockchainBase

logger = logging.getLogger(__name__)


class FileBlockchain(BlockchainBase):

    def __init__(self, base_directory, validate=True):
        if not os.path.isabs(base_directory):
            raise ValueError('base_directory must be an absolute path')

        self.base_directory = base_directory

        self.storage = FileSystemStorage()

        if validate:
            self.validate()

    def iter_account_root_files(self) -> Generator[AccountRootFile, None, None]:
        raise NotImplementedError
