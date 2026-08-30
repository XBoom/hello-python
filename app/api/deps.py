from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ErrorCode
from app.core.exceptions import ForbiddenError, NotFoundError, UnauthorizedError
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.services.auth import AuthService
from app.services.user import UserService

bearer_scheme = HTTPBearer(auto_error=False)

DbSession = Annotated[AsyncSession, Depends(get_db)]


def get_user_service(db: DbSession) -> UserService:
    return UserService(db)


def get_auth_service(db: DbSession) -> AuthService:
    return AuthService(db)


UserSvc = Annotated[UserService, Depends(get_user_service)]
AuthSvc = Annotated[AuthService, Depends(get_auth_service)]


async def get_current_user(
    db: DbSession,
    creds: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ] = None,
) -> User:
    if creds is None or creds.scheme.lower() != "bearer":
        raise UnauthorizedError()
    user_id: UUID = decode_token(creds.credentials, "access")
    try:
        user = await UserService(db).get(user_id)
    except NotFoundError as exc:
        raise UnauthorizedError() from exc
    if not user.is_active:
        raise UnauthorizedError(ErrorCode.INACTIVE_USER, "账号已被禁用")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise ForbiddenError()
    return current_user


SuperUser = Annotated[User, Depends(get_current_superuser)]
