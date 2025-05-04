from enum import Enum
import requests

from logdash.logger.internal_logger import internal_logger
from logdash.metrics.base_metrics import BaseMetrics
from logdash.types.initialization_params import RequiredInitializationParams


class MetricOperation(str, Enum):
    SET = "set"
    CHANGE = "change"


class Metrics(BaseMetrics):
    def __init__(self, params: RequiredInitializationParams):
        self.params = params

    def set(self, name: str, value: float) -> None:
        if self.params.verbose:
            internal_logger.verbose(f"Setting metric {name} to {value}")

        requests.put(
            f"{self.params.host}/metrics",
            headers={
                "Content-Type": "application/json",
                "project-api-key": self.params.api_key,
            },
            json={
                "name": name,
                "value": value,
                "operation": MetricOperation.SET,
            },
        )

    def mutate(self, name: str, value: float) -> None:
        if self.params.verbose:
            internal_logger.verbose(f"Mutating metric {name} by {value}")

        requests.put(
            f"{self.params.host}/metrics",
            headers={
                "Content-Type": "application/json",
                "project-api-key": self.params.api_key,
            },
            json={
                "name": name,
                "value": value,
                "operation": MetricOperation.CHANGE,
            },
        ) 