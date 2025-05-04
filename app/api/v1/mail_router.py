from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter
from pydantic import EmailStr

from app.core.settings import settings
from app.services.mail_service import MailService

router = APIRouter(prefix="/mail", tags=["Mail"])


@router.post(
    "/request-confirmation-code/",
    dependencies=[
        Depends(
            RateLimiter(
                times=1, milliseconds=settings.smtp.confirmation_email_code_rate_limit
            )
        )
    ],
)
async def request_confirmation_code(
    service: Annotated[MailService, Depends()], email: EmailStr
):
    return await service.send_confirmation_email(email)


@router.post("/confirm/")
async def confirm(
    service: Annotated[MailService, Depends()], email: EmailStr, code: int
):
    return await service.confirm(email=email, code=code)
