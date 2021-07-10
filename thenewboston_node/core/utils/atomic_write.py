import contextlib
import shutil
from pathlib import Path

import atomicwrites


@contextlib.contextmanager
def atomic_write_append(file_path, mode, **kwargs):
    append = 'a' in mode
    if append:
        kwargs.setdefault('overwrite', True)
    with atomicwrites.atomic_write(file_path, mode=mode.replace('a', 'w'), **kwargs) as fo:
        # TODO(abo) MEDIUM: append may be slow, probably switch to OS-level file copying
        if append and Path(file_path).exists():
            with open(file_path, 'rb' if 'b' in mode else 'r') as cur_fo:
                shutil.copyfileobj(cur_fo, fo)
        yield fo
