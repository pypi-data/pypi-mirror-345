from enum import StrEnum
from typing import Any, Dict, Generic, Optional, TypedDict, TypeVar

T = TypeVar("T", bound=StrEnum)


class SpryxErrorDict(TypedDict):
    error: str
    message: str
    details: Dict[str, Any]


class SpryxError(Exception, Generic[T]):
    def __init__(
        self,
        code: T,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.code: T = code
        self.message: str = message
        self.details: Dict[str, Any] = details or {}

    def to_dict(self) -> SpryxErrorDict:
        return SpryxErrorDict(
            error=self.code.value,
            message=self.message,
            details=self.details,
        )
