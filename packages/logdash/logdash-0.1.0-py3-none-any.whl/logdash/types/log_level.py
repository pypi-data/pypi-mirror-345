from enum import Enum


class LogLevel(str, Enum):
    ERROR = "error"
    WARN = "warning"
    INFO = "info"
    HTTP = "http"
    VERBOSE = "verbose"
    DEBUG = "debug"
    SILLY = "silly" 