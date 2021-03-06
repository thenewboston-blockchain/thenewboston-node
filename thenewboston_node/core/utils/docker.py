import os
import os.path


def is_in_docker():
    return os.getenv('IN_DOCKER') == 'true' or os.path.isfile('/.dockerenv')
