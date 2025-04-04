from fastapi import HTTPException, status
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


async def authenticate_user(fake_db, username: str, password: str):
    from domains.auth.services.user import user_service

    user = await user_service.get_user_by_username(fake_db, username)
    if not user: raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect Username or Password"
    )
    if not user.is_active: raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Account is suspended"
    )
    if not pwd_context.verify(password, user.password): raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect Username or Password"
    )
    return user
