from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import EmailStr

from app.services.mail_service import MailService

router = APIRouter(prefix="/mail", tags=["Mail"])


@router.post("/request-confirmation-code/")
async def request_confirmation_code(
    service: Annotated[MailService, Depends()], email: EmailStr
):
    return await service.send_confirmation_email(email)


@router.post("/confirm/")
async def confirm(
    service: Annotated[MailService, Depends()], email: EmailStr, code: int
):
    return await service.confirm(email=email, code=code)
