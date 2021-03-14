from enum import Enum, unique


@unique
class NodeType(Enum):
    NODE = 'NODE'
    PRIMARY_VALIDATOR = 'PRIMARY_VALIDATOR'
