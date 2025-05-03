from passlib.context import CryptContext

BCRYPT = "bcrypt"
PasswordType = str | bytes

pwd_context = CryptContext([BCRYPT], deprecated="auto")


def hash_password(password: PasswordType) -> str:
    return pwd_context.hash(password, BCRYPT)


def verify_password(
    plain_password: PasswordType,
    hashed_password: PasswordType,
) -> bool:
    return pwd_context.verify(plain_password, hashed_password, BCRYPT)
