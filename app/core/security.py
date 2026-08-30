from datetime import UTC, datetime, timedelta
from typing import Any, Literal
from uuid import UUID

import jwt
from pwdlib import PasswordHash

from app.core.config import settings
from app.core.constants import ErrorCode
from app.core.exceptions import UnauthorizedError

_hasher = PasswordHash.recommended()

TokenType = Literal["access", "refresh"]


def hash_password(plain: str) -> str:
    return _hasher.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _hasher.verify(plain, hashed)


def create_token(subject: str, token_type: TokenType, expires_delta: timedelta) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: UUID) -> str:
    return create_token(
        str(user_id),
        "access",
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: UUID) -> str:
    return create_token(
        str(user_id),
        "refresh",
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str, expected_type: TokenType) -> UUID:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError as exc:
        raise UnauthorizedError(ErrorCode.TOKEN_EXPIRED, "登录已过期") from exc
    except jwt.InvalidTokenError as exc:
        raise UnauthorizedError(ErrorCode.TOKEN_INVALID, "无效的令牌") from exc

    if payload.get("type") != expected_type:
        raise UnauthorizedError(ErrorCode.TOKEN_INVALID, "令牌类型不正确")

    subject = payload.get("sub")
    if not subject:
        raise UnauthorizedError(ErrorCode.TOKEN_INVALID, "无效的令牌")

    try:
        return UUID(subject)
    except ValueError as exc:
        raise UnauthorizedError(ErrorCode.TOKEN_INVALID, "无效的令牌") from exc
