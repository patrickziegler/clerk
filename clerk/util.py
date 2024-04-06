import sys

def remove_file(filepath, missing_ok=True):
    if sys.version_info.major >= 3 and sys.version_info.minor >= 8:
        import pathlib
        pathlib.Path(filepath).unlink(missing_ok=missing_ok)
    else:
        import os
        try:
            os.remove(filepath)
        except FileNotFoundError:
            if not missing_ok:
                raise
