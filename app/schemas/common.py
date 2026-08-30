from typing import Any

from pydantic import BaseModel, Field

from app.core.constants import ErrorCode


class Response[T](BaseModel):
    code: int = ErrorCode.SUCCESS
    message: str = "success"
    data: T | None = None


class PageResult[T](BaseModel):
    items: list[T]
    total: int
    page: int
    page_size: int


def ok(data: Any = None, message: str = "success") -> dict[str, Any]:
    return {"code": ErrorCode.SUCCESS, "message": message, "data": data}


class PaginationQuery(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
