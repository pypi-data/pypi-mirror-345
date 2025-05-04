from colorama import Fore, Style

from logdash.logger.logger import Logger
from logdash.types.log_level import LogLevel


def logdash_prefix(level: LogLevel) -> str:
    return f"{Fore.MAGENTA}[LogDash] {Style.RESET_ALL}"


internal_logger = Logger(log_method=print, prefix=logdash_prefix) 