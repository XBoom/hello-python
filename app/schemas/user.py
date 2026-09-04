from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "alice@example.com",
                "password": "password123",
                "full_name": "Alice",
            }
        }
    )

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=100)


class UserLogin(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "alice@example.com",
                "password": "password123",
            }
        }
    )

    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=100)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    is_active: bool | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "5f3d2c8e-1a4b-4d6f-9c2a-1b6e7f8a9b0c",
                "email": "alice@example.com",
                "full_name": "Alice",
                "is_active": True,
                "is_superuser": False,
                "created_at": "2026-01-15T10:30:00+08:00",
                "updated_at": "2026-01-15T10:30:00+08:00",
            }
        },
    )

    id: UUID
    email: EmailStr
    full_name: str | None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime