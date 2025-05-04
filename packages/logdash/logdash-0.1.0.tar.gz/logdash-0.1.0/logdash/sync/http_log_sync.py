import requests

from logdash.sync.log_sync import LogSync
from logdash.types.initialization_params import RequiredInitializationParams
from logdash.types.log_level import LogLevel


class HttpLogSync(LogSync):
    def __init__(self, params: RequiredInitializationParams):
        self.params = params
        self.sequence_number = 0

    # todos:
    # - queue
    # - retry
    # - batching
    def send(self, message: str, level: LogLevel, created_at: str) -> None:
        requests.post(
            f"{self.params.host}/logs",
            headers={
                "Content-Type": "application/json",
                "project-api-key": self.params.api_key,
            },
            json={
                "message": message,
                "level": level,
                "createdAt": created_at,
                "sequenceNumber": self.sequence_number,
            },
        )
        self.sequence_number += 1 