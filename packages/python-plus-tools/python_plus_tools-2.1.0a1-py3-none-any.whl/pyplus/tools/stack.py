from queue import Queue, SimpleQueue
from collections import deque
from typing import TypeAlias
from advancedlib.itertools import IteratorCalculator, IteratorRange


class FIFOStack:
    def __init__(self):
        self.stacks = []

    def put(self, items):
        self.stacks.append(items)

    def push(self):
        return self.stacks.pop(0)

    def get(self):
        return self.push()

    @property
    def is_empty(self):
        return len(self.stacks) == 0

    def __sizeof__(self):
        return len(self)

    def __len__(self):
        return len(self.stacks)

    def __repr__(self):
        return f"Stack({",".join(self.stacks)})"

    def __str__(self):
        return self.__repr__()

    def __add__(self, value):
        out_list = self.stacks.append(value)
        o = FIFOStack()
        o.stacks = out_list
        return o


class ThreadFIFOStack(Queue):
    def push(self, items):
        self.stacks.append(items)

    def __sizeof__(self):
        return len(self)

    def __len__(self):
        return len(self.stacks)

    def __repr__(self):
        return f"Stack({",".join(self.stacks)})"

    def __str__(self):
        return self.__repr__()


class LIFOStack:
    def __init__(self):
        self.stacks = []

    def put(self, items):
        self.stacks.append(items)

    def push(self):
        return self.stacks.pop()

    def get(self):
        return self.push()

    @property
    def is_empty(self):
        return len(self.stacks) == 0

    def __sizeof__(self):
        return len(self)

    def __len__(self):
        return len(self.stacks)

    def __repr__(self):
        return f"Stack({",".join(self.stacks)})"

    def __str__(self):
        return self.__repr__()

    def __add__(self, value):
        out_list = self.stacks.append(value)
        o = FIFOStack()
        o.stacks = out_list
        return o


class ThreadLIFOStack(SimpleQueue):
    def push(self, items):
        self.stacks.append(items)

    def __sizeof__(self):
        return len(self)

    def __len__(self):
        return len(self.stacks)

    def __repr__(self):
        return f"Stack({",".join(self.stacks)})"

    def __str__(self):
        return self.__repr__()


class IteratorCalculator:
    def __init__(self, num):
        self.number = num

    def __iter__(self):
        return self

    def __next__(self):
        """Same as self.number -= 1"""
        if self.number == 0:
            raise StopIteration
        self.number -= 1
        return self.number

    def change_number(self, func, value):
        self.number = func(self.number, value)
        return self.number

    def get_number(self):
        return self.number

    def __sizeof__(self):
        return len(self)

    def __len__(self):
        return self.number

    def __repr__(self):
        return f"IteratorCalculator({self.number})"

    def __str__(self):
        return self.__repr__()

    def __add__(self, value):
        out_list = self.number + value
        o = IteratorCalculator(out_list)
        return o

    def __sub__(self, value):
        out_list = self.number - value
        o = IteratorCalculator(out_list)
        return o

    def __mul__(self, value):
        out_list = self.number * value
        o = IteratorCalculator(out_list)
        return o

    def __truediv__(self, value):
        out_list = self.number / value
        o = IteratorCalculator(out_list)
        return o

    def __floordiv__(self, value):
        out_list = self.number // value
        o = IteratorCalculator(out_list)
        return o

    def __mod__(self, value):
        out_list = self.number % value
        o = IteratorCalculator(out_list)
        return o

    def __pow__(self, value):
        out_list = self.number**value
        o = IteratorCalculator(out_list)
        return o

    def __lshift__(self, value):
        out_list = self.number << value
        o = IteratorCalculator(out_list)
        return o

    def __rshift__(self, value):
        out_list = self.number >> value
        o = IteratorCalculator(out_list)
        return o

    def __and__(self, value):
        out_list = self.number & value
        o = IteratorCalculator(out_list)
        return o

    def __xor__(self, value):
        out_list = self.number ^ value
        o = IteratorCalculator(out_list)
        return o

    def __or__(self, value):
        out_list = self.number | value
        o = IteratorCalculator(out_list)
        return o

    def __radd__(self, value):
        self.number += value
        return self

    def __rsub__(self, value):
        self.number -= value
        return self

    def __rmul__(self, value):
        self.number *= value
        return self

    def __rtruediv__(self, value):
        self.number /= value
        return self

    def __rfloordiv__(self, value):
        self.number //= value
        return self

    def __rmod__(self, value):
        self.number %= value
        return self

    def __rpow__(self, value):
        self.number **= value
        return self

    def __rlshift__(self, value):
        self.number <<= value
        return self

    def __rrshift__(self, value):
        self.number >>= value
        return self

    def __rand__(self, value):
        self.number &= value
        return self

    def __rxor__(self, value):
        self.number ^= value
        return self

    def __ror__(self, value):
        self.number |= value
        return self


Stack: TypeAlias = LIFOStack

del TypeAlias
