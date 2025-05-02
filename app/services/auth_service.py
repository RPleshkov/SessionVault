from datetime import timedelta
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_service import RedisService, get_redis
from app.core.settings import settings
from app.database.models import Session, User
from app.database.session import get_session
from app.repository.session import (
    delete_session_by_session_id,
    get_session_by_session_id,
    get_sessions_by_user_id,
)
from app.repository.user import get_user_by_email, get_user_by_id
from app.schemas.token import TokenPairSchema
from app.services.token_service import TokenService
from app.services.utils import check_password


class AuthService:
    def __init__(
        self,
        redis: Annotated[RedisService, Depends(get_redis)],
        db_session: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        self.db_session = db_session
        self.redis = redis

    async def get_active_user(self, user_id: str) -> User:
        user = await get_user_by_id(self.db_session, user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User inactive",
            )

        return user

    async def login(
        self, email: str, password: str, user_agent: str
    ) -> TokenPairSchema:
        user = await get_user_by_email(self.db_session, email)
        if not user or not check_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User inactive",
            )

        token_service = TokenService(user)  # Инициализируем структуру JWT

        sessions = await get_sessions_by_user_id(
            self.db_session, user.id
        )  # Получаем все сессии пользователя в порядке возрастания last_active

        if len(sessions) == settings.app.user_session_limit:
            await self.db_session.delete(
                sessions[0]
            )  # Удаляем самую старую, с точки зрения активности, сессию из БД, если их на текущий момент 5

        new_session = Session(
            user_id=user.id,
            session_id=token_service.sid,
            user_agent=user_agent,
            last_active=token_service.iat,
            expire_at=token_service.refresh_exp,
        )

        self.db_session.add(new_session)
        await self.db_session.commit()

        return TokenPairSchema(
            access_token=token_service.access_token,
            refresh_token=token_service.refresh_token,
        )

    async def logout(self, access_token: str) -> None:
        payload = TokenService.decode_jwt(access_token)

        session_id = payload["sid"]

        await self.redis.set(
            name=f"blacklist_access_token:{session_id}",
            value="revoked",
            ex=timedelta(milliseconds=settings.jwt.access_token_expire_ms),
        )

        await delete_session_by_session_id(self.db_session, session_id)

    async def logout_others(self, access_token: str) -> None:
        payload = TokenService.decode_jwt(access_token)

        session_id = payload["sid"]
        user_id = payload["sub"]
        statement = select(Session).where(
            and_(Session.user_id == user_id, Session.session_id != session_id)
        )
        sessions = (await self.db_session.execute(statement)).scalars().all()
        for session in sessions:
            await self.redis.set(
                name=f"blacklist_access_token:{session.session_id}",
                value="revoked",
                ex=timedelta(milliseconds=settings.jwt.access_token_expire_ms),
            )
            await self.db_session.delete(session)
        await self.db_session.commit()

    async def refresh_tokens(
        self, refresh_token: str, user_agent: str
    ) -> TokenPairSchema:
        payload = TokenService.decode_jwt(refresh_token)

        if payload["purpose"] != "refresh_token":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        user_id = payload["sub"]
        old_session_id = payload["sid"]

        session = await get_session_by_session_id(self.db_session, old_session_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        user = await self.get_active_user(user_id)
        token_service = TokenService(user)

        statement = (
            update(Session)
            .where(Session.session_id == old_session_id)
            .values(
                session_id=token_service.sid,
                last_active=token_service.iat,
                user_agent=user_agent,
                expire_at=token_service.refresh_exp,
            )
        )

        await self.db_session.execute(statement)
        await self.db_session.commit()

        return TokenPairSchema(
            access_token=token_service.access_token,
            refresh_token=token_service.refresh_token,
        )

    async def get_access_token_payload(self, access_token: str) -> dict[str, Any]:
        payload = TokenService.decode_jwt(access_token)

        if payload["purpose"] != "access_token":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        session_id = payload["sid"]
        token_is_revoked = await self.redis.get(
            name=f"blacklist_access_token:{session_id}"
        )
        if token_is_revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        return payload

    async def get_current_user(self, access_token: str) -> User:
        payload = await self.get_access_token_payload(access_token)
        user_id = payload["sub"]
        user = await self.get_active_user(user_id)
        return user
