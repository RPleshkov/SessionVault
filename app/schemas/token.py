from pydantic import BaseModel


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class AccessTokenSchema(BaseModel):
    access_token: str
    type: str = "bearer"


class TokenPairSchema(RefreshTokenSchema, AccessTokenSchema):
    access_token: str
    refresh_token: str
    type: str = "bearer"
