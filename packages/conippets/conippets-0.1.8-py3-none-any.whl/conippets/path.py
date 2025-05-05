import os, shutil

def rm(path, missing_ok=False):
    try:
        os.remove(path)
    except FileNotFoundError:
        if not missing_ok:
            raise

def rmdir(dir, missing_ok=False):
    shutil.rmtree(dir, ignore_errors=missing_ok)