import bcrypt


@staticmethod
def hash_pasword(password: str) -> bytes:
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt(),
    )


@staticmethod
def check_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(
        password.encode(),
        hashed_password,
    )
