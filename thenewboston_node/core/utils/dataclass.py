import inspect

OVERRIDING_METHOD_PREFIX = 'override_'
OVERRIDING_METHOD_PREFIX_LEN = len('override_')


def fake_super_methods(cls):
    # We have to do this black magic because dataclass_json is implemented
    # as decorator, not as base class

    for method_name, method in inspect.getmembers(cls, lambda x: (inspect.isfunction or inspect.ismethod)):
        if not method_name.startswith(OVERRIDING_METHOD_PREFIX):  # skip regular methods
            continue

        actual_name = method_name[OVERRIDING_METHOD_PREFIX_LEN:]

        super_method = getattr(cls, actual_name, None)
        if super_method:
            setattr(cls, 'super_' + actual_name, super_method)  # rename base method, so it can be called

        try:
            method.__name__ = actual_name
        except AttributeError:
            pass

        assert method.__qualname__.endswith('.' + method_name)
        try:
            method.__qualname__ = method.__qualname__[:-len(method_name)] + actual_name
        except AttributeError:
            pass

        setattr(cls, actual_name, method)  # rename method to actual name (without prefix)
        delattr(cls, method_name)  # remove original method (with prefix)

    return cls
