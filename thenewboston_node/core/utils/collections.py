from typing import Callable, Union


def deep_update(base_dict, update_with):
    for key, value in update_with.items():
        if isinstance(value, dict):
            base_dict_value = base_dict.get(key)
            if isinstance(base_dict_value, dict):
                deep_update(base_dict_value, value)
            else:
                base_dict[key] = value
        else:
            base_dict[key] = value

    return base_dict


def replace_keys(source: Union[dict, list], replace_map: dict):
    if isinstance(source, dict):
        return {replace_map.get(key, key): replace_keys(value, replace_map) for key, value in source.items()}

    if isinstance(source, list):
        return [replace_keys(item, replace_map) for item in source]

    return source


def map_values(source: Union[dict, list], replace_map: dict[str, Callable], current_key=None, subkeys=False):
    func = replace_map.get(current_key, noop)

    if isinstance(source, dict):
        if not subkeys:
            func = noop

        return {
            func(key): map_values(value, replace_map, current_key=key, subkeys=subkeys)
            for key, value in source.items()
        }

    if isinstance(source, (list, tuple)):
        return [map_values(item, replace_map, current_key=current_key, subkeys=subkeys) for item in source]

    return func(source)


def noop(val):
    return val
