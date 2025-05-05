import decorators
from img_fit import latex2text as latex

from . import (
    colors,
    dec,
    database_convert,
    formula,
    geohash,
    # password,
    permission,
    pydebugger,
    stack,
    tag,
    type,
    update,
    web,
    variables,
    pycppio,
)
from argparse import Namespace

# from . import () # deprecated moudle


def wait(operator: bool):
    """
    Please use it in subprocess.
    """
    while operator:
        pass
