from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ErrorCode
from app.core.exceptions import UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models.user import User
from app.schemas.token import TokenPair
from app.schemas.user import UserCreate, UserLogin
from app.services.user import UserService


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.users = UserService(session)

    async def register(self, payload: UserCreate) -> User:
        return await self.users.create(payload)

    async def login(self, payload: UserLogin) -> TokenPair:
        user = await self.users.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise UnauthorizedError(ErrorCode.BAD_CREDENTIALS, "邮箱或密码错误")
        if not user.is_active:
            raise UnauthorizedError(ErrorCode.INACTIVE_USER, "账号已被禁用")
        return self._issue_tokens(user.id)

    async def refresh(self, refresh_token: str) -> TokenPair:
        user_id = decode_token(refresh_token, "refresh")
        user = await self.users.get(user_id)
        if not user.is_active:
            raise UnauthorizedError(ErrorCode.INACTIVE_USER, "账号已被禁用")
        return self._issue_tokens(user.id)

    @staticmethod
    def _issue_tokens(user_id: UUID) -> TokenPair:
        return TokenPair(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )
