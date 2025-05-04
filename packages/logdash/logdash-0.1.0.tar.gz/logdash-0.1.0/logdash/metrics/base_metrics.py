from abc import ABC, abstractmethod


class BaseMetrics(ABC):
    @abstractmethod
    def set(self, key: str, value: float) -> None:
        pass

    @abstractmethod
    def mutate(self, key: str, value: float) -> None:
        pass 