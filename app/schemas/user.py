from pydantic import BaseModel, EmailStr, Field, UUID4


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserResponse(UserBase):
    id: UUID4
