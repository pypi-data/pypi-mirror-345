from decimal import Decimal as long
from fractions import Fraction as fraction
from pyplus.tools.dec import dint, SimpleType, Calc

import math
import matplotlib
import numpy as np
import numpy

from sympy import *


def safe_formula_solver(formula, **variables):
    allowed_symbols = {k: symbols(k) for k in variables.keys()}
    try:
        expr = sympify(formula, locals=allowed_symbols)
        return float(expr.subs(variables))
    except SympifyError:
        raise ValueError("Invalid formula")


def joseph_problem(n: int) -> int:
    """
    Joseph problem is a classic problem in computer science. It is a problem of finding the last person standing in a circle of people. The problem is named after the Greek mathematician Josephus. The problem can be solved using a simple algorithm called the Josephus problem. The algorithm works as follows:

    1. Start with a list of n people numbered from 1 to n.
    2. Start with a pointer to the first person in the list.
    3. Remove the person pointed to by the pointer.
    4. Move the pointer n-1 positions ahead in the list.
    5. Repeat steps 3 and 4 until there is only one person left in the list.
    6. The last person remaining in the list is the last person standing in the circle.

    The Josephus problem is a classic example of a mathematical problem that can be solved using a simple algorithm. The algorithm is simple and easy to understand, but it can be improved by using more advanced techniques such as dynamic programming or memoization.
    Args:
        n (int): The number of people in the circle.
    Returns:
        int: The number of the last person standing in the circle.
    """
    if n == 1:
        return 1
    else:
        return (joseph_problem(n - 1) + n - 1) % n + 1
