from abc import ABC, abstractmethod
from typing import Tuple

class AbstractState(ABC):
    @abstractmethod
    def get_state(self) -> Tuple:
        pass