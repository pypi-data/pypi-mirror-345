from datetime import datetime
from typing import Dict, Optional, TypedDict, Any

from logdash.logger.logger import Logger
from logdash.metrics.base_metrics import BaseMetrics
from logdash.metrics.create_metrics import create_metrics
from logdash.sync.create_log_sync import create_log_sync
from logdash.types.initialization_params import InitializationParams, RequiredInitializationParams
from logdash.types.log_level import LogLevel


class LogdashInstance(TypedDict):
    logger: Logger
    metrics: BaseMetrics


def create_logdash(params: Optional[Dict[str, Any]] = None) -> LogdashInstance:
    init_params = InitializationParams()
    
    if params is not None:
        if "api_key" in params:
            init_params.api_key = params["api_key"]
        if "host" in params:
            init_params.host = params["host"]
        if "verbose" in params:
            init_params.verbose = params["verbose"]
    
    required_params = RequiredInitializationParams(
        api_key=init_params.api_key or "",
        host=init_params.host or "https://api.logdash.io",
        verbose=init_params.verbose or False,
    )
    
    log_sync = create_log_sync(required_params)
    metrics = create_metrics(required_params)

    def on_log(level: LogLevel, message: str) -> None:
        log_sync.send(message, level, datetime.now().isoformat())

    return {
        "logger": Logger(log_method=print, on_log=on_log),
        "metrics": metrics,
    } 