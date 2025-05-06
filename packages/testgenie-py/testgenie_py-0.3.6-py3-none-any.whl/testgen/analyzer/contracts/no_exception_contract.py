from testgen.analyzer.contracts.contract import Contract
from abc import ABC

class NoExceptionContract(Contract, ABC):
    """Ensures function does not raise an exception"""

    def check_preconditions(self, args) -> bool:
        """Returns False if there is a violation"""
        return True

    """Returns False if there is an exception"""
    def check_postconditions(self, args, output, exception) -> bool:
        if exception is not None:
            return True
        else:
            return False