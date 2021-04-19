from copy import deepcopy


def factory(dataclass):

    def factory_decorator(factory_class):

        def make_instance(*args, **kwargs):
            for key, val in factory_class.__dict__.items():
                if key.startswith('__') and key.endswith('__'):
                    continue
                kwargs.setdefault(key, deepcopy(val))

            return dataclass(*args, **kwargs)

        return make_instance

    return factory_decorator
