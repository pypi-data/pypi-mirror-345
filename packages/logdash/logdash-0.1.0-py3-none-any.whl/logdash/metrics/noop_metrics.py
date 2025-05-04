from logdash.metrics.base_metrics import BaseMetrics


class NoopMetrics(BaseMetrics):
    def set(self, key: str, value: float) -> None:
        pass

    def mutate(self, key: str, value: float) -> None:
        pass 