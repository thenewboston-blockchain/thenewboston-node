from importlib import import_module


def import_from_string(fully_qualified_name: str):
    module_name, class_name = fully_qualified_name.rsplit('.', 1)
    module_ = import_module(module_name)
    return getattr(module_, class_name)
