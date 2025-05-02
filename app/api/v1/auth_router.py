from typing import Annotated

from fastapi import APIRouter, Depends, Header, status
from fastapi.security import HTTPBearer, OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.schemas.token import RefreshTokenSchema, TokenPairSchema
from app.services.auth_service import AuthService

http_bearer = HTTPBearer(auto_error=False)
oaut2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/")
router = APIRouter(
    prefix="/auth", tags=["Authentication"], dependencies=[Depends(http_bearer)]
)


@router.post(
    "/login/",
    responses={
        200: {"description": "Successfully authenticated"},
        401: {"description": "Invalid credentials"},
        403: {"description": "User inactive"},
    },
)
async def login(
    service: Annotated[AuthService, Depends()],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_agent: Annotated[str, Header()] = "uknown",
) -> TokenPairSchema:
    return await service.login(
        email=form_data.username,
        password=form_data.password,
        user_agent=user_agent,
    )


@router.post(
    "/logout/",
    responses={
        204: {"description": "Successful logout"},
        401: {"description": "Invalid or expired token"},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    service: Annotated[AuthService, Depends()],
    access_token: Annotated[str, Depends(oaut2_scheme)],
):
    await service.logout(access_token=access_token)


@router.post(
    "/logout-others/",
    responses={
        204: {"description": "Successful logout"},
        401: {"description": "Invalid or expired token"},
    },
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout_others(
    service: Annotated[AuthService, Depends()],
    access_token: Annotated[str, Depends(oaut2_scheme)],
):
    await service.logout_others(access_token=access_token)


@router.post(
    "/refresh/",
    responses={
        200: {"description": "Tokens successfully refreshed"},
        401: {"description": "Invalid or expired token"},
        403: {"description": "User inactive"},
        404: {"description": "User not found"},
    },
)
async def refresh(
    service: Annotated[AuthService, Depends()],
    refresh_token: RefreshTokenSchema,
    user_agent: Annotated[str, Header()] = "uknown",
) -> TokenPairSchema:
    return await service.refresh_tokens(
        refresh_token=refresh_token.refresh_token,
        user_agent=user_agent,
    )


@router.get(
    "/me",
    responses={
        200: {"description": "Returns authenticated user data"},
        401: {"description": "Invalid or expired token"},
        403: {"description": "User inactive"},
        404: {"description": "User not found"},
    },
)
async def get_me(
    service: Annotated[AuthService, Depends()],
    access_token: Annotated[str, Depends(oaut2_scheme)],
):
    return await service.get_current_user(access_token)
