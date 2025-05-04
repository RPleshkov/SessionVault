from random import SystemRandom

import bcrypt

from app.core.settings import settings


def hash_pasword(password: str) -> bytes:
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt(),
    )


def check_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(
        password.encode(),
        hashed_password,
    )


def generate_confirmation_email_code() -> int:
    random = SystemRandom()
    code = "".join(
        [
            str(random.randint(0, 9))
            for _ in range(settings.smtp.confirmation_email_code_length)
        ],
    )
    return int(code)
