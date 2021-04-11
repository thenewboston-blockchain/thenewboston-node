from enum import Enum, unique


@unique
class NodeType(Enum):
    REGULAR_NODE = 'REGULAR_NODE'
    PRIMARY_VALIDATOR = 'PRIMARY_VALIDATOR'
