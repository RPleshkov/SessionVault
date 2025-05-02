from typing import TYPE_CHECKING, Sequence
from uuid import UUID

from sqlalchemy import asc, delete, select

from app.database.models import Session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_session_by_session_id(
    session: "AsyncSession", session_id: str
) -> Session | None:
    statement = select(Session).where(Session.session_id == session_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def get_sessions_by_user_id(
    session: "AsyncSession",
    user_id: str | UUID,
) -> Sequence["Session"]:
    statement = (
        select(Session)
        .where(Session.user_id == user_id)
        .order_by(asc(Session.last_active))
    )

    sessions = (await session.execute(statement)).scalars().all()
    return sessions


async def delete_session_by_session_id(
    session: "AsyncSession",
    session_id: str,
) -> None:
    statement = delete(Session).where(Session.session_id == session_id)
    await session.execute(statement)
    await session.commit()
