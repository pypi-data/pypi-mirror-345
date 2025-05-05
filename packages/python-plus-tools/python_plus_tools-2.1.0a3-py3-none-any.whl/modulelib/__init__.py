from importlib import *

from toml import load, dump
from site import getsitepackages

with open(
    getsitepackages()[1] + "/pyplus/data/config/module_config.toml", encoding="utf-8"
) as f:
    config = load(f)

if not config["advancedlib"]["itertools"]["initializinged"]:
    from . import all_module

del load, dump, getsitepackages


def get_import_moudle_path():
    from sys import modules

    if __name__ != "__main__":
        main_moudle = modules["__main__"]
        if hasattr(main_moudle, "__file__"):
            return main_moudle.__file__
        else:
            return None
