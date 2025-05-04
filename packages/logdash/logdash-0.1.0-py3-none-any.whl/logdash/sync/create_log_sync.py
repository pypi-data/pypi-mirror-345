from logdash.logger.internal_logger import internal_logger
from logdash.sync.http_log_sync import HttpLogSync
from logdash.sync.log_sync import LogSync
from logdash.sync.noop_log_sync import NoopLogSync
from logdash.types.initialization_params import RequiredInitializationParams


def create_log_sync(params: RequiredInitializationParams) -> LogSync:
    if not params.api_key:
        internal_logger.log(
            "Api key was not provided in the InitializationParams when calling create_logdash(), using only local logger.\n"
        )
        return NoopLogSync()

    return HttpLogSync(params) 