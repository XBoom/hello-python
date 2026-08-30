from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ErrorCode
from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = UserRepository(session)

    async def get(self, user_id: UUID) -> User:
        user = await self.repo.get(user_id)
        if user is None:
            raise NotFoundError(ErrorCode.USER_NOT_FOUND, "用户不存在")
        return user

    async def get_by_email(self, email: str) -> User | None:
        return await self.repo.get_by_email(email)

    async def list_users(self, *, offset: int, limit: int) -> tuple[list[User], int]:
        items, total = await self.repo.list_ordered(offset=offset, limit=limit)
        return list(items), total

    async def create(self, payload: UserCreate, *, is_superuser: bool = False) -> User:
        if await self.repo.get_by_email(payload.email):
            raise ConflictError(ErrorCode.EMAIL_EXISTS, "邮箱已被注册")
        user = User(
            email=payload.email,
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name,
            is_superuser=is_superuser,
        )
        return await self.repo.create(user)

    async def update(self, user_id: UUID, payload: UserUpdate) -> User:
        user = await self.get(user_id)
        data = payload.model_dump(exclude_unset=True)
        if "password" in data and data["password"]:
            data["hashed_password"] = hash_password(data.pop("password"))
        else:
            data.pop("password", None)
        return await self.repo.update(user, data)
