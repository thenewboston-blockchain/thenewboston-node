from enum import Enum, unique


@unique
class BlockType(Enum):
    COIN_TRANSFER = 'ct'
    NODE_DECLARATION = 'nd'
