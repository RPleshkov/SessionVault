from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class UpdatedAtMixin:
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_onupdate=func.now(),
    )


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
