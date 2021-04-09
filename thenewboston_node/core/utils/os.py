import os


def remove_quite(path):
    try:
        os.remove(path)
    except Exception:
        pass


def chmod_quite(path, mode):
    try:
        os.chmod(path, mode)
    except Exception:
        pass
