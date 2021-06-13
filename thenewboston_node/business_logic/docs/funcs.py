import textwrap
import typing
from inspect import getdoc
from typing import get_type_hints

import class_doc

from thenewboston_node.core.utils.dataclass import is_optional

TYPE_NAME_MAP = {
    'str': 'string',
    'int': 'integer',
    'dict': 'object',
    'list': 'array',
    'tuple': 'array',
}


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
