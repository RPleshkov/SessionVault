from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.settings import settings

engine = create_async_engine(
    url=settings.postgres.get_url,
    pool_size=settings.postgres.pool_size,
    max_overflow=settings.postgres.max_overflow,
    echo=settings.postgres.echo,
)

session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session
