import typing


def is_optional(type_):
    return typing.get_origin(type_) is typing.Union and type(None) in typing.get_args(type_)
