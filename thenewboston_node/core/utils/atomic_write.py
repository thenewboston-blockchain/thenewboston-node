import contextlib
import os
import shutil
import stat
from pathlib import Path

import atomicwrites


@contextlib.contextmanager
def atomic_write_append(file_path, mode, create_perms=0o644, **kwargs):
    append = 'a' in mode
    if append:
        kwargs.setdefault('overwrite', True)
    with atomicwrites.atomic_write(file_path, mode=mode.replace('a', 'w'), **kwargs) as fo:
        # TODO(abo) MEDIUM: append may be slow, probably switch to OS-level file copying
        if append and Path(file_path).exists():
            with open(file_path, 'rb' if 'b' in mode else 'r') as cur_fo:
                shutil.copyfileobj(cur_fo, fo)

            st_mode = os.stat(file_path).st_mode
        else:
            st_mode = stat.S_IMODE(create_perms)
        os.fchmod(fo.fileno(), st_mode)
        yield fo
