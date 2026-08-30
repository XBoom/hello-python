from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_ordered(
        self, *, offset: int, limit: int
    ) -> tuple[Sequence[User], int]:
        stmt = select(User).order_by(User.created_at.desc())
        return await self.list(offset=offset, limit=limit, extra=stmt)
