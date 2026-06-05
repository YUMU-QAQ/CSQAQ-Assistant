"""Common schemas: pagination, error responses, standard envelope."""
from pydantic import BaseModel
from typing import TypeVar, Generic, Optional, Any

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response envelope."""
    code: int = 0
    message: str = "success"
    data: Optional[T] = None

    @classmethod
    def ok(cls, data: Any = None, message: str = "success") -> "ApiResponse":
        return cls(code=0, message=message, data=data)

    @classmethod
    def error(cls, code: int, message: str) -> "ApiResponse":
        return cls(code=code, message=message, data=None)


class PaginatedData(BaseModel):
    total: int
    page: int
    page_size: int
    items: list


class PaginatedResponse(ApiResponse[PaginatedData]):
    pass
