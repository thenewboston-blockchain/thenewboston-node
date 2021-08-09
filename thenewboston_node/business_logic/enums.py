from enum import Enum, unique


@unique
class NodeRole(Enum):
    PRIMARY_VALIDATOR = 1
    CONFIRMATION_VALIDATOR = 2
    REGULAR_NODE = 3
