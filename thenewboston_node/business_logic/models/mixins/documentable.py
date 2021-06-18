import textwrap
import typing
from inspect import getdoc

import class_doc

from thenewboston_node.core.utils.misc import humanize_snake_case

from .base import BaseMixin


def extract_attribute_docs(model):
    docs = {}
    for class_ in reversed(model.mro()):
        if class_ is not object:
            docs |= class_doc.extract_docs_from_cls_obj(cls=class_)

    return docs


class DocumentableMixin(BaseMixin):
    attribute_docs = None

    @classmethod
    def get_nested_models(cls, known_models=(), include_self=False):
        assert cls not in known_models
        known_models = known_models or []
        if include_self:
            known_models.append(cls)

        for field_name in cls.get_field_names():
            field_type = cls.get_field_type(field_name)
            if issubclass(field_type, DocumentableMixin) and field_type not in known_models:
                known_models = field_type.get_nested_models(known_models, include_self=True)
            else:
                origin = typing.get_origin(field_type)
                if origin and issubclass(origin, list):
                    (item_type,) = typing.get_args(field_type)
                    if issubclass(item_type, DocumentableMixin) and item_type not in known_models:
                        known_models = item_type.get_nested_models(known_models, include_self=True)
                elif origin and issubclass(origin, dict):
                    item_key_type, item_value_type = typing.get_args(field_type)
                    if issubclass(item_key_type, DocumentableMixin) and item_key_type not in known_models:
                        known_models = item_key_type.get_nested_models(known_models, include_self=True)
                    if issubclass(item_value_type, DocumentableMixin) and item_value_type not in known_models:
                        known_models = item_value_type.get_nested_models(known_models, include_self=True)

        return known_models

    @classmethod
    def get_docstring(cls):
        return getdoc(cls)

    @classmethod
    def get_field_docstring(cls, field_name, imply_field_name=True):
        if (attribute_docs := cls.attribute_docs) is None:
            cls.attribute_docs = attribute_docs = extract_attribute_docs(cls)

        docstrings = attribute_docs.get(field_name)
        if docstrings:
            return textwrap.dedent(' '.join(docstrings))
        elif imply_field_name:
            return humanize_snake_case(field_name)

        return None
