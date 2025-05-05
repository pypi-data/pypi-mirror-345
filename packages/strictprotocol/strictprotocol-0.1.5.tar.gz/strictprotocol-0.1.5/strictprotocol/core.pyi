from typing import Any
from strictprotocol import CheckMode

class StrictProtocol:
    def __init_subclass__(cls, *, mode: CheckMode = ..., raise_exception: bool = ..., **kwargs: Any) -> None: ...