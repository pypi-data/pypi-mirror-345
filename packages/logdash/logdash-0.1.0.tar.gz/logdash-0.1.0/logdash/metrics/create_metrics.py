from logdash.logger.internal_logger import internal_logger
from logdash.metrics.base_metrics import BaseMetrics
from logdash.metrics.metrics import Metrics
from logdash.metrics.noop_metrics import NoopMetrics
from logdash.types.initialization_params import RequiredInitializationParams


def create_metrics(params: RequiredInitializationParams) -> BaseMetrics:
    if not params.api_key:
        internal_logger.log(
            "Api key was not provided in the InitializationParams when calling create_logdash(), metrics will not be registered.\n"
        )
        return NoopMetrics()

    return Metrics(params) 