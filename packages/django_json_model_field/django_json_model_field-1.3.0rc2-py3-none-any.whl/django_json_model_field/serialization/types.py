from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class JSONModelDict(Protocol):

    def as_db_json(self) -> JSONClassWrapper | dict[str, Any]:
        ...


class JSONClassWrapper:
    """
    Wrapper class to allow classes that are natively JSON serializable to be deserialized to a different class.

    Must be used with JSONModelEncoder and JSONModelDecoder.

    This is helpful for subclasses of dicts that would otherwise be deserialized to a standard dict.
    """

    def __init__(self, wraps: type, data: dict[str, Any]):
        self.data = data
        self.wraps = wraps
