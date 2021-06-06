import typing

from thenewboston_node.core.utils.dataclass import is_optional

NONE_TYPE = type(None)


class BaseMixin:

    @classmethod
    def get_field_names(cls):
        return tuple(cls.__dataclass_fields__.keys())

    @classmethod
    def get_field_type(cls, field_name):
        type_ = cls.__dataclass_fields__[field_name].type
        if typing.get_origin(type_) is typing.Union:
            type_args = [arg for arg in typing.get_args(type_) if arg is not NONE_TYPE]
            assert len(type_args) == 1, 'Multitype fields are not supported'
            type_ = type_args[0]

        return type_

    @classmethod
    def is_optional_field(cls, field_name):
        return is_optional(cls.__dataclass_fields__[field_name].type)
