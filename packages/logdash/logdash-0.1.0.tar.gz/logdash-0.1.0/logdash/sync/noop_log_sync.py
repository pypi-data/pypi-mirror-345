from logdash.sync.log_sync import LogSync
from logdash.types.log_level import LogLevel


class NoopLogSync(LogSync):
    def send(self, message: str, level: LogLevel, created_at: str) -> None:
        pass 