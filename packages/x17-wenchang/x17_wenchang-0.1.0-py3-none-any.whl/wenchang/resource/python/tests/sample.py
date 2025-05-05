# sample.py

import os
import sys
from typing import List, Dict



CONSTANT = 42

class BaseClass:
    """This is a base class."""
    def base_method(self, value: int) -> (int, str):
        """Base method"""
        return value, "result"

class ChildClass(BaseClass):
    """This is a child class inheriting BaseClass."""

    class InnerClass:
        """Nested class inside another class."""
        pass

    def __init__(self, name: str):
        self.name = name

    def child_method(self, param: str) -> str:
        """Child method"""
        return param

@staticmethod
def standalone_function(x: int, y: int = 10) -> int:
    """A standalone function outside classes."""
    return x + y

async def async_function(data: List[int]) -> List[int]:
    """An asynchronous function."""
    return [i * 2 for i in data]

# test_sample_full_ast.py

import os
from typing import List, Dict

x = 1
y = 2
z = x + y
a, b = y, z
c += 1
d: int = 5
del x

def outer(u: int, v=3, *args, **kwargs):
    '''outer function'''
    if u > v:
        return u
    elif v > u:
        return v
    else:
        pass

    while u > 0:
        u -= 1
    for i in range(10):
        print(i)
    with open('file.txt') as f:
        content = f.read()
    try:
        risky()
    except ValueError as e:
        raise e
    finally:
        print("done")

    match u:
        case 1: print("one")
        case _: print("other")

    print("done")
    return u

class Sample(Base):
    class_attr: str = "Hello"
    def method(self):
        return self.class_attr


def gen():
    yield 42

result = lambda x: x * 2
comp = [i for i in range(5)]
s = {1, 2, 3}
d = {k: v for k, v in zip(range(3), range(3))}