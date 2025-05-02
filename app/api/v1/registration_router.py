from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.database.session import get_session
from app.repository.user import create_user, get_user_by_email
from app.schemas.user import UserCreate, UserResponse

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/registration", tags=["Registration"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def registration(
    session: Annotated["AsyncSession", Depends(get_session)],
    user_in: UserCreate,
):
    user = await get_user_by_email(session, user_in.email)

    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )

    return await create_user(session, user_in)
