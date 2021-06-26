import typing

NONE_TYPE = type(None)


def unwrap_optional(type_):
    if typing.get_origin(type_) is typing.Union:
        type_args = [arg for arg in typing.get_args(type_) if arg is not NONE_TYPE]
        if len(type_args) == 1:
            type_ = type_args[0]
    return type_
