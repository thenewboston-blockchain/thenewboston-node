import random
from dataclasses import is_dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional, Union

from dataclass_bakery.generators import defaults, random_data_class_generator
from dataclass_bakery.generators.random_generator import RandomGenerator


class RandomDatetimeGenerator(RandomGenerator):

    def generate(self, *args, **kwargs) -> datetime:
        return datetime.now(timezone.utc)


class RandomHexGenerator(RandomGenerator):
    """
    Implemetation is based on
    https://github.com/miguelFLG13/dataclass-bakery/blob/main/src/dataclass_bakery/generators/random_str_generator.py

    (!!!) This docstring must be kept for legal purposes.
    """

    def generate(self, *args, **kwargs) -> str:
        max_length = kwargs.get(defaults.MAX_LENGTH_ARG, defaults.MAX_STR_LENGTH)
        random_choices = random.choices('01234567890abcdef', k=max_length)
        return ''.join(random_choices)


TYPING_GENERATORS = defaults.TYPING_GENERATORS.copy()
TYPING_GENERATORS[datetime] = RandomDatetimeGenerator
TYPING_GENERATORS[str] = RandomHexGenerator
defaults.TYPING_GENERATORS = TYPING_GENERATORS


class RandomDataClassGenerator:
    """
    Implemetation is based on
    https://github.com/miguelFLG13/dataclass-bakery/blob/main/src/dataclass_bakery/generators/random_data_class_generator.py

    (!!!) This docstring must be kept for legal purposes.
    """

    def generate(self, data_class: Any, *args, **kwargs) -> Any:  # noqa: C901
        random_data = {}
        for field_name, metadata in data_class.__dataclass_fields__.items():
            field_type = metadata.type

            arguments = kwargs.get(field_name, {})
            if defaults.FIXED_VALUE_ARG in arguments:  # Value fixed
                random_data[field_name] = arguments[defaults.FIXED_VALUE_ARG]
                continue

            if defaults.GENERATOR_ARG in arguments:  # Generator fixed
                generator = arguments[defaults.GENERATOR_ARG]()
                field_randomized = generator.generate(**arguments)
                random_data[field_name] = field_randomized
                continue

            if getattr(field_type, '__origin__', None) == Union:
                has_new_type = False
                for argument in field_type.__args__:
                    if argument != type(None):  # noqa: E721
                        has_new_type = True
                        field_type = argument

                    if not hasattr(field_type, '__origin__') or field_type.__origin__ != Union:
                        break

                if not has_new_type:
                    raise TypeError(f'Union without Typing in dataclass {field_name}')

            if getattr(field_type, '__origin__', None) == dict:
                arguments[defaults.KEY_TYPE_ARG] = field_type.__args__[0]
                arguments[defaults.VALUE_TYPE_ARG] = field_type.__args__[1]
                field_type = field_type.__origin__
            elif getattr(field_type, '__origin__', None) in (list, tuple):
                arguments[defaults.VALUE_TYPE_ARG] = field_type.__args__[0]
                field_type = field_type.__origin__
            elif getattr(field_type, '__origin__', None) == Literal:
                arguments[defaults.OPTIONS_ARG] = field_type.__args__
                field_type = field_type.__origin__

            if is_dataclass(field_type):
                generator = RandomDataClassGenerator()
                field_randomized = generator.generate(field_type, **arguments)
            else:
                generator_class = TYPING_GENERATORS.get(field_type)
                generator = generator_class()
                field_randomized = generator.generate(**arguments)

            random_data[field_name] = field_randomized

        return data_class(**random_data)


random_data_class_generator.RandomDataClassGenerator = RandomDataClassGenerator


def make(
    _data_class: Any,
    _quantity: int = 1,
    _attr_defaults: Optional[Dict] = None,
    **kwargs,
) -> Union[List, Any]:
    """
    Implemetation is based on
    https://github.com/miguelFLG13/dataclass-bakery/blob/main/src/dataclass_bakery/baker.py

    (!!!) This docstring must be kept for legal purposes.
    """

    _attr_defaults = _attr_defaults or {}
    for key, value in kwargs.items():
        _attr_defaults[key] = {'_fixed_value_': value}

    random_data_class_generator = RandomDataClassGenerator()

    data_class_objects = []
    for _ in range(_quantity):
        data_class_object = random_data_class_generator.generate(_data_class, **_attr_defaults)
        data_class_objects.append(data_class_object)

    if len(data_class_objects) == 1:
        return data_class_objects[0]

    return data_class_objects
