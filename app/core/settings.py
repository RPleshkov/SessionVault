from dataclasses import dataclass, field
from pathlib import Path

from environs import Env
from pydantic import PostgresDsn

env = Env()
env.read_env()
CERTS_PATH = Path(__file__).parent / "certs"


@dataclass
class PostgresConfig:
    host: str = env("POSTGRES_HOST")
    db_name: str = env("POSTGRES_DB_NAME")
    user: str = env("POSTGRES_USER")
    password: str = env("POSTGRES_PASSWORD")
    port: int = env.int("POSTGRES_PORT")

    pool_size: int = 20
    max_overflow: int = 5
    echo: bool = False

    def __post_init__(self):
        self.naming_convention: dict[str, str] = {
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }

    @property
    def get_url(self):
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                host=self.host,
                port=self.port,
                username=self.user,
                password=self.password,
                path=self.db_name,
            )
        )


@dataclass
class RedisConfig:
    host: str = env("REDIS_HOST")
    port: int = env.int("REDIS_PORT")
    password: str = env("REDIS_PASSWORD")
    user: str = env("REDIS_USER")
    db: str = env("REDIS_DB")


@dataclass
class JWTConfig:
    algorithm: str = "RS256"
    private_key: Path = CERTS_PATH / "private.pem"
    public_key: Path = CERTS_PATH / "public.pem"
    access_token_expire_ms: int = env.int("ACCESS_TOKEN_EXPIRE_MS")
    refresh_token_expire_ms: int = env.int("REFRESH_TOKEN_EXPIRE_MS")


@dataclass
class AppConfig:
    user_session_limit: int = env.int("USER_SESSION_LIMIT")


@dataclass(frozen=True)
class Config:
    postgres: PostgresConfig = field(default_factory=PostgresConfig)
    jwt: JWTConfig = field(default_factory=JWTConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    app: AppConfig = field(default_factory=AppConfig)


settings = Config()
