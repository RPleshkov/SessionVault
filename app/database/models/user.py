from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import Base
from app.database.models.mixins import CreatedAtMixin, UpdatedAtMixin

if TYPE_CHECKING:
    from app.database.models.session import Session


class UserRole(Enum):
    admin = "admin"
    moderator = "moderator"
    user = "user"


class User(Base, CreatedAtMixin, UpdatedAtMixin):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[bytes] = mapped_column(BYTEA)
    role: Mapped[UserRole] = mapped_column(default=UserRole.user)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_verified: Mapped[bool] = mapped_column(default=False)

    sessions: Mapped[list["Session"]] = relationship(back_populates="user")
