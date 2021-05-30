from enum import Enum, unique

from .signed_change_request import CoinTransferSignedChangeRequest


@unique
class BlockType(Enum):
    COIN_TRANSFER = 'ct'


REQUEST_TO_BLOCK_TYPE_MAP = {
    CoinTransferSignedChangeRequest: BlockType.COIN_TRANSFER.value,
}
