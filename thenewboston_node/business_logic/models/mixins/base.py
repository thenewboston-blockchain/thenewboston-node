import dataclasses
import typing

from thenewboston_node.core.utils.typing import unwrap_optional


class BaseMixin:
    _field_cache: typing.ClassVar = {}

    @classmethod
    def get_fields(cls):
        fields = cls._field_cache.get(cls)
        if fields is None:
            fields = {field.name: field for field in dataclasses.fields(cls)}
            cls._field_cache[cls] = fields
        return fields

    @classmethod
    def get_field(cls, field_name):
        return cls.get_fields()[field_name]

    @classmethod
    def get_field_names(cls):
        return cls.get_fields().keys()

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

    @classmethod
    def get_field_metadata(cls, field_name):
        return cls.get_field(field_name).metadata

    @classmethod
    def is_serializable_field(cls, field_name):
        return cls.get_field_metadata(field_name).get('is_serializable', True)
