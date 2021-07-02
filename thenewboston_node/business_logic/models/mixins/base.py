import dataclasses
import typing

from thenewboston_node.core.utils.typing import unwrap_optional


class BaseMixin:

    @classmethod
    def get_fields(cls):
        return dict((f.name, f) for f in dataclasses.fields(cls))

    @classmethod
    def get_field(cls, field_name):
        return cls.get_fields()[field_name]

    @classmethod
    def get_field_names(cls):
        return tuple(cls.get_fields().keys())

    @classmethod
    def get_field_type(cls, field_name):
        type_ = cls.get_field(field_name).type
        type_ = unwrap_optional(type_)
        assert type_ is not typing.Union, 'Multitype fields are not supported'

        return type_

    @classmethod
    def is_optional_field(cls, field_name):
        type_ = cls.get_field(field_name).type
        return typing.get_origin(type_) is typing.Union and type(None) in typing.get_args(type_)
