import string
from typing import List

class TestCase:
    def __init__(self, func_name, inputs: tuple, expected: any):
        self.func_name = func_name
        self.inputs = inputs
        self.expected = expected