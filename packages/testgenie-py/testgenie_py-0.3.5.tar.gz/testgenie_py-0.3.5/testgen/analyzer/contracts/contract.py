from abc import ABC, abstractmethod

class Contract(ABC):
    @abstractmethod
    def check_preconditions(self, args) -> bool:
        """Check preconditions before the method executes."""
        pass

    @abstractmethod
    def check_postconditions(self, args, output, exception) -> bool:
        """Check postconditions before the method executes."""
        pass

