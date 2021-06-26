from typing import Union


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
