from dataclasses import dataclass
from typing import Optional


@dataclass
class InitializationParams:
    api_key: Optional[str] = None
    host: Optional[str] = None
    verbose: Optional[bool] = None


@dataclass
class RequiredInitializationParams:
    api_key: str
    host: str
    verbose: bool 