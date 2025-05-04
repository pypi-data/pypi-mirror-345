from abc import ABC, abstractmethod

from logdash.types.log_level import LogLevel


class LogSync(ABC):
    @abstractmethod
    def send(self, message: str, level: LogLevel, created_at: str) -> None:
        pass 