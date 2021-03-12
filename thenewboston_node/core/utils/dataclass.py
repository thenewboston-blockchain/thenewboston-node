import inspect


def fake_super_methods(cls):
    # We have to do this black magic because dataclass_json is implemented
    # as dectorator, not as base class

    for name, method in inspect.getmembers(cls, lambda x: (inspect.isfunction or inspect.ismethod)):
        if not name.startswith('override_'):
            continue

        new_name = name[len('override_'):]

        # Move super method
        super_method = getattr(cls, new_name, None)
        if super_method:
            setattr(cls, 'super_' + new_name, super_method)

        # Move overriding method
        try:
            method.__name__ = new_name
        except AttributeError:
            pass

        assert method.__qualname__.endswith('.' + name)
        try:
            method.__qualname__ = method.__qualname__[:-len(name)] + new_name
        except AttributeError:
            pass

        setattr(cls, new_name, method)
        delattr(cls, name)

    return cls
