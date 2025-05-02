from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import jwt
from fastapi import HTTPException, status

from app.core.settings import settings
from app.database.models import User


class TokenService:

    algorithm = settings.jwt.algorithm
    private_key = settings.jwt.private_key.read_text()
    public_key = settings.jwt.public_key.read_text()
    access_token_expire_ms = settings.jwt.access_token_expire_ms
    refresh_token_expire_ms = settings.jwt.refresh_token_expire_ms

    def __init__(self, user: User) -> None:
        self._access_token = None
        self._refresh_token = None
        self.sub = user.id
        self.role = user.role.value
        self.iat = datetime.now(timezone.utc)
        self.sid = uuid4()
        self.access_exp = self.iat + timedelta(
            milliseconds=self.access_token_expire_ms,
        )
        self.refresh_exp = self.iat + timedelta(
            milliseconds=self.refresh_token_expire_ms
        )

    def encode_jwt(self, payload: dict[str, Any]) -> str:
        to_encode = payload.copy()

        if to_encode["purpose"] == "access_token":
            exp = self.access_exp
        if to_encode["purpose"] == "refresh_token":
            exp = self.refresh_exp

        to_encode.update(
            sub=str(self.sub),
            sid=str(self.sid),
            iat=self.iat,
            exp=exp,
        )

        return jwt.encode(
            payload=to_encode,
            key=self.private_key,
            algorithm=self.algorithm,
        )

    @classmethod
    def decode_jwt(cls, token: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(
                jwt=token,
                key=cls.public_key,
                algorithms=[cls.algorithm],
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        return payload

    @property
    def access_token(self) -> str:
        if self._access_token is None:
            payload = {
                "purpose": "access_token",
                "role": self.role,
            }
            self._access_token = self.encode_jwt(payload)
        return self._access_token

    @property
    def refresh_token(self) -> str:
        if self._refresh_token is None:

            payload = {
                "purpose": "refresh_token",
            }
            self._refresh_token = self.encode_jwt(payload)
        return self._refresh_token
