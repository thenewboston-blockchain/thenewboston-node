import logging
import os

import yaml

logger = logging.getLogger(__name__)


def yaml_coerce(value):
    if isinstance(value, str):
        return yaml.load('dummy: ' + value, Loader=yaml.SafeLoader)['dummy']

    return value


def get_settings_from_environment(prefix):
    prefix_len = len(prefix)
    return {key[prefix_len:]: yaml_coerce(value) for key, value in os.environ.items() if key.startswith(prefix)}
