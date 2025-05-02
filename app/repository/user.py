from typing import TYPE_CHECKING

from sqlalchemy import select

from app.database.models import User
from app.schemas.user import UserCreate
from app.services.utils import hash_pasword

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_by_email(session: "AsyncSession", email: str) -> User | None:
    statement = select(User).where(User.email == email)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def get_user_by_id(session: "AsyncSession", user_id: str) -> User | None:
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def create_user(session: "AsyncSession", user_in: UserCreate) -> User:

    user = User(
        name=user_in.name,
        email=user_in.email.lower(),
        password=hash_pasword(user_in.password),
    )

    session.add(user)
    await session.commit()
    return user
