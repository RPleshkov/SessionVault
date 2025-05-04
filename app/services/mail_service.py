from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from httpx import delete
from pydantic import EmailStr

from app.core.redis_service import RedisService, get_redis
from app.core.settings import settings
from app.database.session import get_session
from app.repository.user import get_user_by_email
from app.services.utils import generate_confirmation_email_code

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

conf = ConnectionConfig(
    MAIL_USERNAME=settings.smtp.username,
    MAIL_PASSWORD=settings.smtp.password,
    MAIL_FROM=settings.smtp.username,
    MAIL_PORT=settings.smtp.port,
    MAIL_SERVER=settings.smtp.host,
    MAIL_FROM_NAME="FastAPI",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates",
)

fm = FastMail(conf)


class MailService:

    def __init__(
        self,
        redis: Annotated[RedisService, Depends(get_redis)],
        db_session: Annotated["AsyncSession", Depends(get_session)],
    ) -> None:
        self.redis = redis
        self.db_session = db_session

    @staticmethod
    async def send_welcome_email(email: EmailStr, name: str) -> None:

        message = MessageSchema(
            subject="Добро пожаловать!",
            recipients=[email],
            template_body={"name": name},
            subtype=MessageType.html,
        )

        await fm.send_message(message, template_name="welcome_email.html")

    async def send_confirmation_email(self, email: EmailStr) -> JSONResponse:

        user = await get_user_by_email(self.db_session, email)
        if not user:
            raise HTTPException(status_code=status.HTTP_200_OK)

        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already confirmed",
            )

        code = generate_confirmation_email_code()

        message = MessageSchema(
            subject="Подтверждение регистрации",
            recipients=[email],
            template_body={
                "name": user.name,
                "confirmation_code": code,
            },
            subtype=MessageType.html,
        )

        await fm.send_message(message, template_name="confirmation_email.html")

        await self.redis.delete(
            name=f"confirmation_code:{email}"
        )  # делаем предыдущий код не валидным (если был)
        await self.redis.set(
            name=f"confirmation_code:{email}",
            value=code,
            ex=timedelta(milliseconds=settings.smtp.confirmation_email_code_ttl),
        )

        return JSONResponse(
            status_code=200, content={"message": "confirmation code has been sent"}
        )

    async def is_valid_confirmation_code(self, email: EmailStr, code: int) -> bool:
        value = await self.redis.get(name=f"confirmation_code:{email}")
        if value is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The confirmation code has expired",
            )
        return value == code

    async def confirm(self, email: EmailStr, code: int) -> JSONResponse:

        user = await get_user_by_email(self.db_session, email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="Email is already confirmed",
            )

        if not (await self.is_valid_confirmation_code(email, code)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid confirmation code or email",
            )

        user.is_verified = True
        await self.redis.delete(name=f"confirmation_code:{email}")
        await self.db_session.commit()
        return JSONResponse(
            status_code=200, content={"message": "Email successfully confirmed"}
        )


