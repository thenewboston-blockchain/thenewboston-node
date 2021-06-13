from thenewboston_node.business_logic.models.base import BaseDataclass

TYPE_NAME_MAP = {
    'str': 'string',
    'hexstr': 'string of hexadecimal characters',
    'int': 'integer',
    'dict': 'object',
    'list': 'array',
    'tuple': 'array',
    'datetime': 'string of ISO formatted datetime'
}


def get_mapped_type_name(type_name):
    return TYPE_NAME_MAP.get(type_name, type_name)


def is_model(type_):
    return issubclass(type_, BaseDataclass)
