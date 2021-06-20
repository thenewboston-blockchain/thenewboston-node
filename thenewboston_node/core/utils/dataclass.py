DUMMY_DOCSTRING = object()


# We have to do cover / revert with 2 decorators to avoid mypy issue
def revert_docstring(cls):
    if cls.__doc__ is DUMMY_DOCSTRING:
        cls.__doc__ = None

    return cls


def cover_docstring(cls):
    if cls.__doc__ is None:
        cls.__doc__ = DUMMY_DOCSTRING

    return cls
