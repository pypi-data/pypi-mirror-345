import os
import pathlib


def get_path_from_env(var_name):
    path = os.getenv(var_name)
    assert path is not None

    path = pathlib.Path(path)
    assert path.exists(), path

    return path
