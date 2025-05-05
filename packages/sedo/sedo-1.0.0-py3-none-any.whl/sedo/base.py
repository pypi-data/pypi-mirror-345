from abc import ABC, abstractmethod
from typing import Any

class BaseOptimizer(ABC):
    @abstractmethod
    def optimize(self, max_iter: int) -> None:
        pass

    @abstractmethod
    def get_best_solution(self) -> Any:
        pass