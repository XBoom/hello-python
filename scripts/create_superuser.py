"""创建超级管理员账号。

用法:
    python -m scripts.create_superuser
    python -m scripts.create_superuser --email admin@example.com --password secret123
"""

from __future__ import annotations

import argparse
import asyncio
from getpass import getpass

from app.db.session import async_session_factory, engine
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate
from app.services.user import UserService


async def create_superuser(email: str, password: str, full_name: str | None) -> User:
    async with async_session_factory() as session:
        repo = UserRepository(session)
        existing = await repo.get_by_email(email)
        if existing:
            if not existing.is_superuser:
                existing.is_superuser = True
                await session.commit()
                print(f"已将已有账号提升为超级管理员: {email}")
                return existing
            print(f"超级管理员已存在: {email}")
            return existing

        user = await UserService(session).create(
            UserCreate(email=email, password=password, full_name=full_name),
            is_superuser=True,
        )
        await session.commit()
        print(f"已创建超级管理员: {user.email}")
        return user


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="创建超级管理员")
    parser.add_argument("--email", help="登录邮箱")
    parser.add_argument("--password", help="登录密码")
    parser.add_argument("--full-name", default="Admin", help="显示名称")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    email = args.email or input("Email: ").strip()
    password = args.password or getpass("Password: ")
    if len(password) < 8:
        raise SystemExit("密码至少 8 位")
    try:
        asyncio.run(create_superuser(email, password, args.full_name))
    finally:
        asyncio.run(engine.dispose())


if __name__ == "__main__":
    main()
