from abc import ABC

from testgen.analyzer.contracts.contract import Contract

class NonNullContract(Contract, ABC):
    """Ensures the function does not contain null or None input values."""
    def check_preconditions(self, args) -> bool:
        return all(arg is not None for arg in args)

    """Ensures the return value is not None"""
    def check_postconditions(self, args, output, exception) -> bool:
        if exception:
            return False
        else:
            return output is not None