import typing
from typing import Any, Optional

from thenewboston_node.business_logic.exceptions import ValidationError
from thenewboston_node.core.utils.misc import coerce_from_json_type, coerce_to_json_type

from .base import BaseMixin


def serialize_value(value, skip_none_values, coerce_to_json_types):  # noqa: C901
    if isinstance(value, SerializableMixin):
        value = value.serialize_to_dict(skip_none_values=skip_none_values, coerce_to_json_types=coerce_to_json_types)
    elif isinstance(value, list):
        new_value = []
        for item in value:
            if isinstance(item, SerializableMixin):
                item = item.serialize_to_dict(
                    skip_none_values=skip_none_values, coerce_to_json_types=coerce_to_json_types
                )
            elif coerce_to_json_types:
                item = coerce_to_json_type(item)

            new_value.append(item)

        value = new_value
    elif isinstance(value, dict):
        new_value = {}
        for item_key, item_value in value.items():
            if isinstance(item_key, SerializableMixin):
                item_key = item_key.serialize_to_dict(
                    skip_none_values=skip_none_values, coerce_to_json_types=coerce_to_json_types
                )
            elif coerce_to_json_types:
                item_key = coerce_to_json_type(item_key)

            if isinstance(item_value, SerializableMixin):
                item_value = item_value.serialize_to_dict(
                    skip_none_values=skip_none_values, coerce_to_json_types=coerce_to_json_types
                )
            elif coerce_to_json_types:
                item_value = coerce_to_json_type(item_value)

            new_value[item_key] = item_value

        value = new_value
    elif coerce_to_json_types:
        value = coerce_to_json_type(value)

    return value


class SerializableMixin(BaseMixin):

    @staticmethod
    def deserialize_from_inner_list(field_type, value, complain_excessive_keys):
        (item_type,) = typing.get_args(field_type)
        new_value = []
        for item in value:
            if issubclass(item_type, SerializableMixin):
                item = item_type.deserialize_from_dict(item, complain_excessive_keys=complain_excessive_keys)
            else:
                item = coerce_from_json_type(item, item_type)

            new_value.append(item)

        return new_value

    @staticmethod
    def deserialize_from_inner_dict(field_type, value, complain_excessive_keys, item_values_override=None):
        item_values_override = item_values_override or {}

        new_value = {}
        item_key_type, item_value_type = typing.get_args(field_type)
        for item_key, item_value in value.items():
            item_key_original = item_key
            if issubclass(item_key_type, SerializableMixin):
                item_key = item_key_type.deserialize_from_dict(
                    item_key, complain_excessive_keys=complain_excessive_keys
                )
            else:
                item_key = coerce_from_json_type(item_key, item_key_type)

            if issubclass(item_value_type, SerializableMixin):
                item_value = item_value_type.deserialize_from_dict(
                    item_value,
                    complain_excessive_keys=complain_excessive_keys,
                    override=item_values_override.get(item_key_original)
                )
            else:
                item_value = coerce_from_json_type(item_value, item_value_type)

            new_value[item_key] = item_value

        return new_value

    @classmethod
    def deserialize_from_dict(
        cls, dict_, complain_excessive_keys=True, override: Optional[dict[str, Any]] = None
    ):  # noqa: C901
        """Return instance deserialized from `dict_`.
        Args:
            dict_ (dict): dict object to be deserialized from
            complain_excessive_keys (bool): if `True` then `ValidationError` is raise if unknown keys are met
            override (dict): a dict of values that have already been deserialized
        """
        override = override or {}
        field_names = set(cls.get_field_names())
        missing_keys = [
            key for key in field_names - dict_.keys() if key not in override and not cls.is_optional_field(key)
        ]
        if missing_keys:
            raise ValidationError('Missing keys: {}'.format(', '.join(missing_keys)))

        deserialized = {}
        for key, value in dict_.items():
            if key in override:
                continue

            if key not in field_names:
                if complain_excessive_keys:
                    raise ValidationError(f'Unknown key: {key}')
                else:
                    continue

            field_type = cls.get_field_type(key)
            if issubclass(field_type, SerializableMixin):
                value = field_type.deserialize_from_dict(value, complain_excessive_keys=complain_excessive_keys)
            else:
                origin = typing.get_origin(field_type)
                if origin and issubclass(origin, list):
                    value = cls.deserialize_from_inner_list(field_type, value, complain_excessive_keys)
                elif origin and issubclass(origin, dict):
                    value = cls.deserialize_from_inner_dict(field_type, value, complain_excessive_keys)
                else:
                    value = coerce_from_json_type(value, field_type)

            deserialized[key] = value

        deserialized.update(override)

        return cls(**deserialized)  # type: ignore

    def serialize_to_dict(self, skip_none_values=True, coerce_to_json_types=True, exclude=()):
        serialized = {}
        for field_name in self.get_field_names():
            if field_name in exclude or not self.is_serializable_field(field_name):
                continue

            value = getattr(self, field_name)
            if value is None and skip_none_values:
                continue

            serialized[field_name] = serialize_value(value, skip_none_values, coerce_to_json_types)

        return serialized
