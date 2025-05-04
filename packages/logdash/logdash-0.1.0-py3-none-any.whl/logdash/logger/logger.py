from datetime import datetime
from typing import Any, Callable, List, Dict, Optional

from colorama import Fore, Style, init

from logdash.types.log_level import LogLevel

# Initialize colorama
init()

LOG_LEVEL_COLORS: Dict[LogLevel, str] = {
    LogLevel.ERROR: Fore.RED,
    LogLevel.WARN: Fore.YELLOW,
    LogLevel.INFO: Fore.BLUE,
    LogLevel.HTTP: Fore.CYAN,
    LogLevel.VERBOSE: Fore.GREEN,
    LogLevel.DEBUG: Fore.LIGHTGREEN_EX,
    LogLevel.SILLY: Fore.LIGHTBLACK_EX,
}


class Logger:
    def __init__(
        self,
        log_method: Callable = print,
        prefix: Optional[Callable[[LogLevel], str]] = None,
        on_log: Optional[Callable[[LogLevel, str], None]] = None,
    ):
        self.log_method = log_method
        self.prefix = prefix or (lambda level: f"{level.value.upper()} ")
        self.on_log = on_log

    def error(self, *data: Any) -> None:
        self._log(LogLevel.ERROR, " ".join(str(item) for item in data))

    def warn(self, *data: Any) -> None:
        self._log(LogLevel.WARN, " ".join(str(item) for item in data))

    def info(self, *data: Any) -> None:
        self._log(LogLevel.INFO, " ".join(str(item) for item in data))

    def log(self, *data: Any) -> None:
        self._log(LogLevel.INFO, " ".join(str(item) for item in data))

    def http(self, *data: Any) -> None:
        self._log(LogLevel.HTTP, " ".join(str(item) for item in data))

    def verbose(self, *data: Any) -> None:
        self._log(LogLevel.VERBOSE, " ".join(str(item) for item in data))

    def debug(self, *data: Any) -> None:
        self._log(LogLevel.DEBUG, " ".join(str(item) for item in data))

    def silly(self, *data: Any) -> None:
        self._log(LogLevel.SILLY, " ".join(str(item) for item in data))

    def _log(self, level: LogLevel, message: str) -> None:
        color = LOG_LEVEL_COLORS[level]
        
        date_prefix = f"{Fore.LIGHTBLACK_EX}[{datetime.now().isoformat()}]{Style.RESET_ALL}"
        prefix = f"{color}{self.prefix(level)}{Style.RESET_ALL}"
        formatted_message = f"{date_prefix} {prefix}{message}"

        self.log_method(formatted_message)
        if self.on_log:
            self.on_log(level, message) 