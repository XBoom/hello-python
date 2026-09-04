from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import ErrorCode


class Response[T](BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": 0,
                "message": "success",
                "data": {"id": "5f3d2c8e-1a4b-4d6f-9c2a-1b6e7f8a9b0c"},
            }
        }
    )

    code: int = ErrorCode.SUCCESS
    message: str = "success"
    data: T | None = None


class PageResult[T](BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 0,
                "page": 1,
                "page_size": 20,
            }
        }
    )

    items: list[T]
    total: int
    page: int
    page_size: int


def ok(data: Any = None, message: str = "success") -> dict[str, Any]:
    return {"code": ErrorCode.SUCCESS, "message": message, "data": data}


class PaginationQuery(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)