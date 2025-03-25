from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


async def authenticate_user(fake_db, username: str, password: str):
    from domains.auth.services.user import user_service

    user = await user_service.get_user_by_username(fake_db, username)
    if not user:
        return False
    if not pwd_context.verify(password, user.password):
        return False
    return user
